"""
Modulo: orchestrator.py
Responsabilità: Agente Supervisore Contesto-Aware — unico punto di contatto tra UI e backend.

Architettura (agente singolo):
    L'orchestratore combina responsabilità conversazionali e di routing in un solo agente.
    Non esiste un layer conversazionale separato: questo agente parla direttamente con
    l'utente E smista il lavoro agli agenti specializzati.

    UI  →  Orchestrator  →  ContentGen / PracticeGen / DB

    Aggiungere un agente separato per la conversazione introdurrebbe:
        - Latenza doppia (due chiamate LLM per ogni messaggio)
        - Un punto di fallimento in più (traduzione intent → JSON)
        - Complessità di debug non giustificata (solo 3 tool)

Gestione della memoria (fix Streamlit):
    In Streamlit le variabili globali vengono distrutte ad ogni rerun della pagina.
    Tutti i singleton (orchestratore, agente teorico) vivono in ``st.session_state``
    per sopravvivere ai rerun e mantenere la memoria conversazionale di LangGraph.

API pubblica:
    - ``chat_con_orchestratore()``: unica funzione chiamata dalle pagine Streamlit.
    - ``aggiorna_contesto_sessione()``: chiamare quando l'utente cambia pagina/corso.
    - ``reset_sessione_chat()``: chiamare al logout.
"""

import sys
import os
import json

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from langchain_core.tools import tool
from platform_sdk.database import db
from platform_sdk.llm import get_llm
from platform_sdk.agent import crea_agente, esegui_agente

from src.agents.content_gen import crea_agente_content_gen, esegui_generazione
from src.agents.practice_gen import esegui_generazione_pratica
from src.agents.gap_analysis import analizza_gap
from src.tools.rag_engine import (
    recupera_sommari_materiali,
    cerca_chunk_rilevanti,
    cerca_chunk_piattaforma,
    conta_chunk_piattaforma,
    formatta_contesto_rag,
    formatta_riferimenti_materiali,
)

# ---------------------------------------------------------------------------
# Chiavi session_state
# ---------------------------------------------------------------------------
_SK_ORCHESTRATORE         = "_orch_agente_compilato"       # studente
_SK_ORCHESTRATORE_DOCENTE = "_orch_agente_docente"         # docente
_SK_AGENTE_TEORICO        = "_orch_agente_teorico"
_SK_THREAD_ID             = "_orch_thread_id"
_SK_CONTESTO              = "_orch_contesto_sessione"

# ---------------------------------------------------------------------------
# Variabile globale thread-safe per studente_id
# ---------------------------------------------------------------------------
# PROBLEMA: LangGraph esegue i tool in thread background (ThreadPoolExecutor).
# In quei thread st.session_state NON è accessibile — restituisce None
# silenziosamente, causando il fallback a studente_id=1 (sempre Giulia).
# Questo è confermato dai warning "missing ScriptRunContext" nel terminale.
#
# SOLUZIONE: variabile globale a livello di modulo Python.
# I moduli Python sono condivisi all'interno dello stesso processo,
# quindi è visibile sia dal thread principale Streamlit che dai thread
# background di LangGraph. Viene aggiornata PRIMA di ogni chiamata
# all'agente, dal thread principale dove session_state funziona.
_STUDENTE_ID_CORRENTE: int = 1

# Stesso pattern per il contesto di navigazione (tipo_vista, corso_id, piano_id…).
# tool_leggi_contesto legge da qui invece che da st.session_state.
_CONTESTO_CORRENTE: dict = {}


def _aggiorna_studente_corrente() -> None: 
    """Legge studente_id da session_state (thread principale) e lo salva
    nella variabile globale, rendendolo disponibile ai thread background."""
    global _STUDENTE_ID_CORRENTE
    sid = (
        st.session_state.get("current_user_id")
        or st.session_state.get("user", {}).get("user_id")
        or st.session_state.get("user", {}).get("id")
    )
    if sid:
        _STUDENTE_ID_CORRENTE = int(sid)


# ---------------------------------------------------------------------------
# System prompt — prompt separati per ruolo (studente / docente)
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT_DOCENTE = """Sei Lea, l'assistente virtuale dei docenti della piattaforma LearnAI.

IL TUO CARATTERE:
Parli in italiano con un tono professionale, diretto e propositivo.
Supporti i docenti nella gestione didattica e nel monitoraggio della classe.
Dopo ogni analisi, proponi sempre azioni concrete di intervento.

COSA SAI FARE (tool a tua disposizione):
1. tool_leggi_contesto       → sapere quale corso è attualmente visualizzato.
2. tool_analizza_classe      → analizzare performance studenti, argomenti più difficili, rischio abbandono.
3. tool_esplora_catalogo     → scoprire corsi, materiali di un corso, o CERCARE materiali per nome.
                                tipo_ricerca='corsi' → lista corsi attivi.
                                tipo_ricerca='argomenti' → materiali di un corso specifico.
                                tipo_ricerca='cerca_materiale' + keyword → cerca materiali per nome
                                tra tutti i materiali del corso e quelli caricati dal docente.
4. tool_genera_corso         → generare una lezione teorica su un argomento del corso.
                                Accetta un parametro opzionale materiale_id per generare
                                la lezione SOLO dal contenuto di quel materiale specifico.
                                IMPORTANTE: genera SEMPRE una lezione da UN SOLO materiale alla volta.
5. tool_genera_pratica       → creare quiz o flashcard per gli studenti.
6. tool_modifica_piano       → leggere e riscrivere il testo di capitoli/paragrafi del corso,
                                rinominare, riordinare, eliminare, aggiungere capitoli e paragrafi.
7. tool_analizza_coerenza_materiali → analizzare la coerenza tematica tra più materiali.
                                Utile per decidere come integrare materiali in un corso esistente.

REGOLE DI COMPORTAMENTO:
- Usa SEMPRE tool_leggi_contesto come PRIMA azione per sapere dove si trova il docente.
- Se tool_leggi_contesto riporta "ANALYTICS del corso: ...", il docente sta guardando le statistiche
  di quel corso. Qualsiasi domanda vaga (andamento, risultati, studenti, quiz, difficoltà) va
  interpretata come riferita a quel corso → chiama tool_analizza_classe con quel corso_id IMMEDIATAMENTE.
- Non chiedere mai "di quale corso parli?" se il contesto già indica un corso nelle analytics.
- Quando il docente chiede "andamento della classe", "studenti in difficoltà", "argomenti ostici",
  "chi è a rischio", "nessuno ha fatto quiz", "risultati" o simili → usa SEMPRE tool_analizza_classe.
- I contenuti generati (lezioni, quiz) sono associati al corso ufficiale.
- Non parlare mai di "piano personalizzato": i docenti gestiscono corsi, non piani.
- Dopo ogni analisi, suggerisci azioni concrete: es. rivedere un argomento, creare esercizi mirati.
- Se il docente non ha ancora studenti o quiz, comunicalo chiaramente e suggerisci come procedere.
- RICERCA MATERIALI PER NOME: quando il docente menziona un materiale o documento per nome
  (es. "il materiale di DeepLearning", "le slide di marketing", "il PDF sulla cybersecurity", ecc.),
  NON chiedere dove si trova. Usa SUBITO tool_esplora_catalogo(tipo_ricerca='cerca_materiale',
  keyword='...') per cercarlo. Se trovi UN solo risultato, usalo direttamente senza chiedere
  conferma. Se trovi più risultati, mostrali e chiedi quale intende. Se non trovi nulla,
  comunicalo e suggerisci di verificare i materiali caricati.
- MODIFICA CONTENUTI DEL CORSO: quando il docente chiede di modificare, riscrivere, semplificare
  o espandere un paragrafo o capitolo del corso:
  1. Chiama tool_leggi_contesto → ottieni il piano_id e la struttura (capitoli e paragrafi con ID).
  2. Identifica il paragrafo_id dal nome (corrispondenza parziale se necessario).
  3. Chiama tool_modifica_piano(piano_id, 'leggi_contenuto', paragrafo_id) per leggere il testo attuale.
  4. Genera il testo riscritto in modo completo e dettagliato.
  5. Chiama tool_modifica_piano(piano_id, 'riscrivi_contenuto', paragrafo_id, nuovo_testo, materiale_id).
     Se hai usato un materiale specifico per arricchire il contenuto, passa il materiale_id
     per tracciare la fonte. Il materiale apparirà in "Materiale del piano".
  NON dire mai che non puoi modificare il contenuto: hai sempre tool_modifica_piano a disposizione.
- ARRICCHIRE UN CORSO CON MATERIALE: quando il docente chiede di arricchire, integrare o ampliare
  un corso usando un materiale specifico, segui lo stesso flusso della modifica ma per contenuti nuovi:
  1. Chiama tool_leggi_contesto → ottieni piano_id e struttura.
  2. Cerca il materiale con tool_esplora_catalogo.
  3. Per ogni nuovo argomento: aggiungi capitolo con 'aggiungi_capitolo',
     poi paragrafi con 'aggiungi_paragrafo', poi scrivi il contenuto con 'riscrivi_contenuto'
     passando SEMPRE il materiale_id per tracciare la fonte.
  NON creare mai capitoli vuoti senza paragrafi.
- Se l'utente fa small talk o saluta, rispondi naturalmente senza invocare tool.
- Se la richiesta è davvero ambigua e non puoi risolvere con una ricerca, fai UNA sola domanda mirata.
- Non mostrare mai ID numerici interni all'utente.
- Gestisci gli errori con empatia e suggerisci il passo successivo.
"""

_SYSTEM_PROMPT = """Sei Lea, il tutor didattico intelligente della piattaforma LearnAI.

IL TUO CARATTERE:
Parli in italiano con un tono caldo, chiaro e motivante. Non sei un bot che esegue
comandi: capisci il contesto, anticipi i bisogni e rendi l'esperienza di studio
piacevole. Dopo ogni azione completata, proponi proattivamente il passo successivo logico.

COSA SAI FARE (tool a tua disposizione):
1. tool_leggi_contesto          → sapere quale corso sta visualizzando lo studente e il piano attivo.
2. tool_esplora_catalogo        → scoprire corsi, materiali di un corso, o CERCARE materiali per nome.
                                  tipo_ricerca='corsi' → lista corsi attivi.
                                  tipo_ricerca='argomenti' → materiali di un corso specifico.
                                  tipo_ricerca='cerca_materiale' + keyword → cerca materiali per nome
                                  tra tutti i materiali dello studente (personali e dei corsi).
3. tool_genera_corso            → creare una nuova lezione teorica su un argomento.
                                  Accetta un parametro opzionale materiale_id per generare
                                  la lezione SOLO dal contenuto di quel materiale specifico.
                                  IMPORTANTE: genera SEMPRE una lezione da UN SOLO materiale alla volta.
4. tool_genera_pratica          → creare quiz, flashcard o schemi su una sezione studiata.
5. tool_analizza_preparazione   → analizzare i risultati di un quiz e identificare lacune.
6. tool_modifica_piano          → rinominare, riordinare, eliminare, aggiungere capitoli/paragrafi,
                                  LEGGERE e RISCRIVERE il testo di una lezione.
7. tool_analizza_coerenza_materiali → analizzare la coerenza tematica tra più materiali.
                                  Utile per decidere come integrare materiali in un piano esistente.
8. tool_genera_corso_libero        → generare una lezione attingendo a TUTTI i materiali della piattaforma
                                  (modalità "Lea sceglie"). Lea cerca autonomamente il materiale più
                                  pertinente tra tutto ciò che è disponibile nel sistema.
                                  Il piano generato include automaticamente i riferimenti bibliografici.
9. tool_rispondi_domanda        → RISPONDERE a domande, dubbi e curiosità dello studente su argomenti,
                                  concetti, paragrafi o capitoli SENZA creare piani o lezioni.
                                  Cerca materiale rilevante con RAG e risponde in modo conversazionale.

REGOLA FONDAMENTALE — RISPONDERE vs GENERARE:
Non tutte le richieste richiedono la creazione di un piano o una lezione!
Quando lo studente fa una DOMANDA o chiede una SPIEGAZIONE, usa tool_rispondi_domanda.
Quando lo studente chiede di CREARE, GENERARE o STUDIARE un argomento in modo strutturato,
usa tool_genera_corso o tool_genera_corso_libero.

Usa tool_rispondi_domanda quando lo studente:
- Fa una domanda su un argomento ("Cos'è il Deep Learning?", "Parlami delle reti neurali")
- Chiede di spiegare un concetto ("Spiegami la normalizzazione", "Come funziona il backpropagation?")
- Chiede esempi ("Fammi un esempio di SQL JOIN")
- Vuole un riassunto ("Riassumi il capitolo X", "Riassumi brevemente questo argomento")
- Ha un dubbio su un paragrafo specifico ("Nel paragrafo X si parla di Y, spiega meglio")
- Chiede chiarimenti ("Non ho capito la differenza tra...", "Cosa si intende per...")
- Fa domande generiche di cultura ("Parlami delle imprese commerciali", "Cos'è il machine learning?")

Se lo studente menziona un paragrafo o capitolo specifico, passa il nome come contesto_aggiuntivo
a tool_rispondi_domanda per recuperare il contenuto esatto dal piano.

MODALITÀ CHAT CON DOCUMENTO:
Quando tool_leggi_contesto riporta "MODALITÀ CHAT CON DOCUMENTO ATTIVA", lo studente
sta chattando su un documento specifico. In questa modalità:
- Usa SEMPRE tool_rispondi_domanda per TUTTE le richieste (anche riassunti, spiegazioni, esempi).
- Passa sempre il nome del documento come contesto_aggiuntivo.
- NON proporre mai di generare piani o lezioni: lo studente vuole interagire col documento.
- NON chiedere su quale corso o materiale vuole lavorare: il documento è già selezionato.
- Se lo studente chiede qualcosa che il documento non copre, rispondi comunque ma segnala
  che l'informazione non proviene dal documento selezionato.

Usa tool_genera_corso / tool_genera_corso_libero SOLO quando lo studente:
- Chiede ESPLICITAMENTE di generare un piano, un corso o una lezione strutturata
- Usa parole come "genera", "crea un piano", "prepara una lezione"
- Vuole materiale di studio organizzato da salvare nel proprio piano personalizzato

REGOLE DI COMPORTAMENTO:
- Ogni messaggio dell'utente è preceduto da un tag [CONTESTO NAVIGAZIONE: ...] che indica
  il contesto ATTUALE della sessione. Questo tag ha SEMPRE la priorità su qualsiasi contesto
  precedente nella cronologia della conversazione. Se il tag dice "Corso 'X'" ma nella cronologia
  precedente eri in modalità chat documento, ignora il vecchio contesto e considera il contesto
  attuale come unica verità. Chiama comunque tool_leggi_contesto per i dettagli completi.
- Usa SEMPRE tool_leggi_contesto come prima azione per capire quale corso è visualizzato.
- I CORSI UNIVERSITARI sono in sola lettura e modificabili SOLO dai docenti. Se lo studente
  chiede di modificare, accorciare, riscrivere o cambiare contenuti di un CORSO universitario,
  rispondi che i corsi non sono modificabili dagli studenti e suggerisci di creare un piano
  personalizzato dove potrà avere la propria versione personalizzata dei contenuti,
  oppure di modificare un piano personalizzato esistente se ne ha già uno.
- I PIANI PERSONALIZZATI sono spazi privati dello studente. Quando generi contenuti,
  stai sempre creando un PIANO PERSONALIZZATO — mai modificando il corso ufficiale.
- RICERCA MATERIALI PER NOME: quando lo studente menziona un materiale, un documento o un
  argomento per nome (es. "il mio materiale di DeepLearning", "le slide di marketing", ecc.),
  NON chiedere dove si trova. Usa SUBITO tool_esplora_catalogo(tipo_ricerca='cerca_materiale',
  keyword='...') per cercarlo. Se trovi UN solo risultato, usalo direttamente senza chiedere
  conferma. Se trovi più risultati, mostrali e chiedi quale intende. Se non trovi nulla,
  comunicalo e suggerisci di controllare i materiali caricati.
- MATERIALE SELEZIONATO (SINGOLO): se tool_leggi_contesto riporta "Materiale selezionato" con
  UN SOLO materiale_id, lo studente vuole una lezione su quel materiale specifico. Usa SUBITO
  tool_genera_corso passando il materiale_id indicato nel contesto. Se non c'è un corso
  associato, usa corso_universitario_id=0. Non chiedere conferme.
- MATERIALI MULTIPLI SELEZIONATI: se tool_leggi_contesto riporta "Materiali selezionati"
  con più materiale_ids, DEVI generare una lezione SEPARATA per CIASCUN materiale.
  NON tentare MAI di combinare più materiali in una sola lezione (causa errori di generazione).
  Flusso OBBLIGATORIO:
  1. Informa lo studente che genererai un piano separato per ogni materiale selezionato.
  2. Per CIASCUN materiale nella lista, chiama tool_genera_corso con il singolo materiale_id
     e corso_universitario_id=0.
  3. Al termine, comunica allo studente che sono stati creati i piani e suggerisci di
     consultarli singolarmente.
  Se lo studente vuole poi unificare i contenuti, suggerisci di creare un piano vuoto
  e usare tool_modifica_piano per integrare i contenuti dei vari piani.
- MATERIALE SENZA CORSO: se lo studente vuole una lezione da materiali personali non legati
  a nessun corso, usa tool_genera_corso con corso_universitario_id=0 e il materiale_id appropriato.
- Quando lo studente chiede di riscrivere, modificare, semplificare, espandere un paragrafo:
  1. Chiama tool_leggi_contesto → ottieni piano_id e l'elenco "Sezioni del piano" con gli ID.
  2. Identifica il paragrafo_id dal nome (corrispondenza parziale se necessario).
  3. Chiama tool_modifica_piano(piano_id, 'leggi_contenuto', paragrafo_id) per leggere il testo attuale.
  4. Genera il testo riscritto in modo completo e dettagliato.
  5. Chiama tool_modifica_piano(piano_id, 'riscrivi_contenuto', paragrafo_id, nuovo_testo, materiale_id).
     Se hai usato un materiale specifico per arricchire il contenuto, passa il materiale_id
     per tracciare la fonte. Il materiale apparirà in "Materiale del piano".
  NON chiedere mai il numero del piano all'utente: è già nel contesto.
  NON dire mai che non puoi modificare il testo: hai sempre questo percorso disponibile.
- ARRICCHIRE UN PIANO CON MATERIALE DIDATTICO: quando lo studente chiede di arricchire,
  integrare o ampliare un piano personalizzato usando un materiale specifico:
  1. Chiama tool_leggi_contesto → ottieni piano_id e la struttura attuale del piano.
  2. Cerca il materiale con tool_esplora_catalogo(tipo_ricerca='cerca_materiale', keyword='...').
  3. Leggi il contenuto del materiale per capire gli argomenti che copre.
  4. Per OGNI argomento rilevante del materiale:
     a. Aggiungi un capitolo: tool_modifica_piano(piano_id, 'aggiungi_capitolo', 0, titolo_capitolo)
        → ottieni il capitolo_id dalla risposta.
     b. Per ogni sotto-argomento, aggiungi un paragrafo:
        tool_modifica_piano(piano_id, 'aggiungi_paragrafo', capitolo_id, titolo_paragrafo)
        → ottieni il paragrafo_id dalla risposta.
     c. Scrivi il contenuto del paragrafo basandoti sul materiale:
        tool_modifica_piano(piano_id, 'riscrivi_contenuto', paragrafo_id, testo_completo, materiale_id)
        IMPORTANTE: passa SEMPRE il materiale_id per tracciare la fonte nel piano.
  NON creare mai capitoli vuoti senza paragrafi. Ogni capitolo DEVE avere almeno un paragrafo con contenuto.
  Se il piano ha già capitoli sugli stessi argomenti, arricchisci quelli esistenti invece di duplicarli.
- MODALITÀ "LEA SCEGLIE" (ricerca su tutta la piattaforma):
  Quando lo studente chiede di GENERARE una lezione su un argomento generico SENZA riferimento
  a un corso specifico o a un materiale specifico, e tool_leggi_contesto NON riporta un corso
  o materiale già selezionato nel contesto:
  1. Offri allo studente 3 opzioni:
     a) Riferirsi a un corso specifico tra quelli a cui è iscritto
     b) Usare il proprio materiale didattico caricato
     c) "Lea sceglie" — tu cercherai tra TUTTI i materiali disponibili sulla piattaforma
  2. Se lo studente sceglie l'opzione c) ("Lea sceglie" o equivalente):
     - Fai al MASSIMO 3 domande di chiarimento per capire:
       * L'argomento specifico (non generico) su cui vuole la lezione
       * Il livello di approfondimento desiderato (introduttivo, intermedio, avanzato)
       * Eventuali aree specifiche da includere o escludere
     - Dopo aver raccolto abbastanza informazioni (o dopo 3 messaggi di chiarimento),
       chiama tool_genera_corso_libero con l'argomento raffinato e le istruzioni raccolte.
     - NON chiedere MAI più di 3 domande: dopo la terza, procedi con le informazioni disponibili.
  3. Il piano generato includerà automaticamente un capitolo "Riferimenti bibliografici"
     con l'elenco dei materiali della piattaforma usati come fonte.
  4. NON attivare questo flusso se c'è già un corso o materiale nel contesto (in quel caso
     usa tool_genera_corso come di consueto).
  5. ATTENZIONE: se lo studente fa solo una DOMANDA (es. "Parlami del Deep Learning") senza
     chiedere di generare un piano, usa tool_rispondi_domanda invece di questo flusso.
- Se l'utente fa small talk o saluta, rispondi naturalmente senza invocare tool.
- Se la richiesta è davvero ambigua e non puoi risolvere con una ricerca, fai UNA sola domanda mirata.
- Non mostrare mai ID numerici interni all'utente.
- Gestisci gli errori con empatia e suggerisci il passo successivo.

REGOLA QUIZ E FLASHCARD — ASSOCIAZIONE OBBLIGATORIA A UN PIANO PERSONALIZZATO:
Quiz e flashcard possono essere generati SOLO per sezioni (paragrafi) di un piano personalizzato.
NON è possibile creare quiz o flashcard "liberi" senza un piano associato.
Quando lo studente chiede di creare quiz, flashcard o strumenti pratici:
1. Chiama tool_leggi_contesto per verificare il contesto attuale.
2. Se lo studente NON ha nessun piano personalizzato:
   - NON generare quiz o flashcard.
   - Spiega che per creare quiz e flashcard è necessario prima generare un piano personalizzato.
   - Proponi di creare un piano personalizzato sull'argomento di interesse.
3. Se lo studente HA piani personalizzati ma NON sta visualizzando un piano specifico
   (tipo_vista ≠ "piano" oppure piano_id è assente nel contesto):
   - NON generare quiz o flashcard direttamente.
   - Chiedi a quale piano personalizzato vuole associare quiz e flashcard.
   - Elenca i piani disponibili (li trovi nell'output di tool_leggi_contesto) per facilitare la scelta.
4. Se lo studente sta visualizzando un piano specifico (tipo_vista="piano" con piano_id presente):
   - Procedi normalmente con tool_genera_pratica per le sezioni del piano attivo.
"""


# ===========================================================================
# Tool
# ===========================================================================

@tool
def tool_leggi_contesto() -> str:
    """
    Leggi il contesto corrente della sessione: corso visualizzato, piano attivo e ultime sezioni generate.
    Usa questo tool PRIMA di chiedere all'utente su quale corso vuole lavorare.
    """
    # Usa il globale di modulo: st.session_state non è accessibile dai thread
    # background di LangGraph (warning "missing ScriptRunContext").
    contesto = _CONTESTO_CORRENTE
    if not contesto:
        # Anche senza contesto attivo, verifica se lo studente ha piani personalizzati
        parti = ["Nessun contesto attivo. L'utente non ha ancora selezionato un corso."]
        studente_id = _STUDENTE_ID_CORRENTE
        if studente_id:
            try:
                piani_studente = db.esegui(
                    "SELECT id, titolo, stato FROM piani_personalizzati "
                    "WHERE studente_id = ? AND stato = 'attivo' ORDER BY id DESC",
                    [studente_id],
                )
                if piani_studente:
                    elenco_piani = "\n".join(
                        f"  - Piano ID {p['id']}: '{p['titolo']}'"
                        for p in piani_studente
                    )
                    parti.append(
                        f"Piani personalizzati dello studente ({len(piani_studente)} attivi):\n{elenco_piani}"
                    )
                else:
                    parti.append(
                        "Lo studente NON ha ancora nessun piano personalizzato. "
                        "Per generare quiz o flashcard è necessario prima creare un piano."
                    )
            except Exception:
                pass
        return "\n".join(parti)

    parti = []
    tipo = contesto.get("tipo_vista")
    if tipo == "docente":
        parti.append("L'utente è un DOCENTE. Usa la modalità docente: analisi classe, gestione corso.")
    elif tipo == "corso":
        parti.append(
            "L'utente sta visualizzando un CORSO universitario (sola lettura). "
            "I corsi NON sono modificabili dagli studenti. Se lo studente chiede di "
            "modificare, accorciare, riscrivere o cambiare qualsiasi contenuto del corso, "
            "rispondi che i corsi sono gestiti dai docenti e non modificabili. "
            "Suggerisci di creare un piano personalizzato per avere una versione propria dei contenuti."
        )
    elif tipo == "piano":
        parti.append("L'utente sta studiando nel proprio PIANO PERSONALIZZATO.")

    if contesto.get("corso_id"):
        nome = contesto.get("corso_nome", "nome non disponibile")
        parti.append(f"Corso: ID {contesto['corso_id']} — {nome}")

    # Analytics filter: il docente sta guardando le statistiche di un corso specifico
    analytics_id = contesto.get("analytics_corso_id")
    analytics_nome = contesto.get("analytics_corso_nome")
    if analytics_id:
        parti.append(
            f"Il docente sta visualizzando le ANALYTICS del corso: ID {analytics_id} — {analytics_nome or 'nome non disponibile'}. "
            f"Se chiede informazioni sull'andamento, i risultati, gli studenti o simili, "
            f"usa tool_analizza_classe con corso_id={analytics_id} SENZA chiedere conferme."
        )

    if contesto.get("piano_id"):
        piano_id = contesto["piano_id"]
        titolo = contesto.get("piano_titolo", "Piano personalizzato")
        parti.append(f"Piano personalizzato attivo: ID {piano_id} — '{titolo}'")

        # Fetch live struttura capitoli+paragrafi dal DB (con capitolo_id per spostamenti).
        try:
            capitoli_db = db.esegui(
                "SELECT id, titolo FROM piano_capitoli WHERE piano_id = ? ORDER BY ordine",
                [piano_id],
            )
            if capitoli_db:
                righe = ["Struttura del piano (capitoli e paragrafi):"]
                for cap in capitoli_db:
                    righe.append(f"  Capitolo ID {cap['id']}: {cap['titolo']}")
                    pp = db.esegui(
                        "SELECT id, titolo FROM piano_paragrafi WHERE capitolo_id = ? ORDER BY ordine",
                        [cap["id"]],
                    )
                    for p in pp:
                        righe.append(f"    - Paragrafo ID {p['id']}: {p['titolo']}")
                parti.append("\n".join(righe))
            else:
                parti.append("Il piano non ha ancora sezioni generate.")
        except Exception:
            # Fallback a ultimi_paragrafi se il DB non è disponibile
            if contesto.get("ultimi_paragrafi"):
                lista = "\n".join(
                    f"  - ID {p['id']}: {p['titolo']}"
                    for p in contesto["ultimi_paragrafi"]
                )
                parti.append(f"Ultime sezioni generate:\n{lista}")

    elif contesto.get("ultimi_paragrafi"):
        lista = "\n".join(
            f"  - ID {p['id']}: {p['titolo']}"
            for p in contesto["ultimi_paragrafi"]
        )
        parti.append(f"Ultime sezioni generate:\n{lista}")

    # Materiale/i selezionato/i dallo studente tramite il pannello "Visualizza materiale"
    materiali_multipli = contesto.get("materiali_selezionati")
    mat = contesto.get("materiale_selezionato")

    if materiali_multipli and len(materiali_multipli) > 1:
        # Più materiali selezionati → genera un piano SEPARATO per ciascuno
        titoli = ", ".join(f"'{m['titolo']}'" for m in materiali_multipli)
        elenco_mat = "\n".join(
            f"  - materiale_id={m['id']}: '{m['titolo']}' (corso_id=0)"
            for m in materiali_multipli
        )
        parti.append(
            f"Materiali selezionati dallo studente (MULTIPLI): {titoli}\n"
            f"{elenco_mat}\n"
            f"IMPORTANTE: genera un piano SEPARATO per CIASCUN materiale. "
            f"Chiama tool_genera_corso una volta per ogni materiale con il singolo materiale_id "
            f"e corso_universitario_id=0. NON combinare più materiali in una sola lezione."
        )
    elif mat:
        corso_id_mat = mat.get("corso_id") or 0  # 0 = nessun corso associato
        # Controlla se siamo in modalità "chat con documento"
        doc_chat = contesto.get("documento_chat")
        if doc_chat:
            parti.append(
                f"⚠️ MODALITÀ CHAT CON DOCUMENTO ATTIVA: lo studente sta chattando sul documento "
                f"'{mat['titolo']}' (materiale_id={mat['id']}). "
                f"NON generare piani o lezioni. Usa SEMPRE tool_rispondi_domanda per rispondere "
                f"alle domande, passando la domanda e il nome del documento come contesto_aggiuntivo. "
                f"Ogni risposta deve basarsi sul contenuto di questo documento specifico."
            )
        else:
            parti.append(
                f"Materiale selezionato dallo studente: '{mat['titolo']}' "
                f"(materiale_id={mat['id']}, corso_id={corso_id_mat}). "
                f"Genera una lezione su questo materiale chiamando tool_genera_corso "
                f"con corso_universitario_id={corso_id_mat} e materiale_id={mat['id']}."
            )

    # Elenco piani personalizzati dello studente (utile per quiz/flashcard)
    tipo = contesto.get("tipo_vista")
    if tipo != "docente":
        studente_id = _STUDENTE_ID_CORRENTE
        try:
            piani_studente = db.esegui(
                "SELECT id, titolo, stato FROM piani_personalizzati "
                "WHERE studente_id = ? AND stato = 'attivo' ORDER BY id DESC",
                [studente_id],
            )
            if piani_studente:
                elenco_piani = "\n".join(
                    f"  - Piano ID {p['id']}: '{p['titolo']}'"
                    for p in piani_studente
                )
                parti.append(
                    f"Piani personalizzati dello studente ({len(piani_studente)} attivi):\n{elenco_piani}"
                )
            else:
                parti.append(
                    "Lo studente NON ha ancora nessun piano personalizzato. "
                    "Per generare quiz o flashcard è necessario prima creare un piano."
                )
        except Exception:
            pass

    return "\n".join(parti) if parti else "Contesto parziale: nessuna sezione generata ancora."


@tool
def tool_esplora_catalogo(tipo_ricerca: str, corso_universitario_id: int = None, keyword: str = "") -> str:
    """
    Scopri i corsi universitari disponibili o cerca materiali didattici.
    - tipo_ricerca='corsi'           → lista tutti i corsi attivi.
    - tipo_ricerca='argomenti'       → materiali del corso (richiede corso_universitario_id).
    - tipo_ricerca='cerca_materiale' → cerca materiali per nome/keyword tra TUTTI i materiali
                                       dello studente (personali e dei corsi). Richiede keyword.
    """
    if tipo_ricerca == "corsi":
        corsi = db.trova_tutti("corsi_universitari", {"attivo": 1})
        if not corsi:
            return "Nessun corso universitario attivo nel sistema."
        return "Corsi disponibili:\n" + "\n".join(
            f"- ID {c['id']}: {c['nome']}" for c in corsi
        )

    elif tipo_ricerca == "cerca_materiale":
        if not keyword or not keyword.strip():
            return "Errore: specifica una keyword per cercare i materiali."
        studente_id = _STUDENTE_ID_CORRENTE
        kw = f"%{keyword.strip()}%"
        risultati = db.esegui(
            "SELECT id, titolo, tipo, corso_universitario_id, is_processed "
            "FROM materiali_didattici "
            "WHERE (docente_id = ? OR corso_universitario_id IN "
            "  (SELECT corso_universitario_id FROM studenti_corsi WHERE studente_id = ?)) "
            "AND titolo LIKE ? "
            "ORDER BY caricato_il DESC",
            [studente_id, studente_id, kw],
        )
        if not risultati:
            return f"Nessun materiale trovato con keyword '{keyword}'."
        righe = [f"Materiali trovati per '{keyword}':"]
        for m in risultati:
            corso_info = f"corso ID {m['corso_universitario_id']}" if m["corso_universitario_id"] else "materiale personale"
            stato = "✅ elaborato" if m.get("is_processed") else "⏳ in attesa"
            righe.append(f"- materiale_id={m['id']}: {m['titolo']} ({m['tipo']}, {corso_info}, {stato})")
        if len(risultati) == 1:
            m = risultati[0]
            righe.append(
                f"\nTrovato UN SOLO materiale. Usalo direttamente con tool_genera_corso "
                f"(corso_universitario_id={m['corso_universitario_id'] or 0}, materiale_id={m['id']})."
            )
        return "\n".join(righe)

    elif tipo_ricerca == "argomenti":
        if not corso_universitario_id:
            return "Errore: specifica corso_universitario_id per vedere gli argomenti."
        materiali = db.trova_tutti(
            "materiali_didattici", {"corso_universitario_id": corso_universitario_id}
        )
        if not materiali:
            return f"Nessun materiale caricato per il corso ID {corso_universitario_id}."
        return (
            f"Materiali del corso ID {corso_universitario_id}:\n"
            + "\n".join(
                f"- materiale_id={m['id']}: {m['titolo']} ({m['tipo']})"
                + (" ✅ elaborato" if m.get("is_processed") else " ⏳ in attesa")
                for m in materiali
            )
            + "\nPer generare una lezione da un materiale specifico, usa tool_genera_corso "
            + "con materiale_id=<id del materiale>."
        )

    return "Errore: tipo_ricerca deve essere 'corsi', 'argomenti' o 'cerca_materiale'."


@tool
def tool_genera_corso(corso_universitario_id: int, argomento: str, materiale_id: int = 0, materiale_ids_csv: str = "", forza_ricerca_keyword: int = 0) -> str:
    """
    Genera e salva un corso teorico completo su un argomento specifico.
    Usa quando l'utente chiede di creare una lezione, un corso o approfondire un tema.

    Parametro corso_universitario_id: usa 0 se non c'è un corso associato (es. materiale personale).
    Parametro opzionale materiale_id: se > 0, la lezione viene generata usando SOLO
    i contenuti di quel materiale specifico (utile quando lo studente ha selezionato
    un documento dal pannello "Visualizza materiale").
    IMPORTANTE: genera SEMPRE una lezione da UN SOLO materiale alla volta.
    Se ci sono più materiali, chiama questo tool una volta per ciascun materiale.
    Parametro materiale_ids_csv: riservato per integrazione in corsi esistenti, non usare
    per generare lezioni nuove da più materiali combinati.
    Parametro forza_ricerca_keyword: usa 1 SOLO se la ricerca semantica è fallita
    e l'utente ha dato il consenso esplicito a procedere con la ricerca per parole chiave
    (meno precisa). Default 0.
    """
    # Usa la variabile globale aggiornata dal thread principale prima dell'invocazione
    studente_id = _STUDENTE_ID_CORRENTE

    # corso_id=0 è il sentinella per "nessun corso": passa None al motore
    corso_id_eff = corso_universitario_id if corso_universitario_id and corso_universitario_id > 0 else None

    # Parsing materiale_ids_csv
    mat_ids: list[int] | None = None
    mat_id_singolo: int | None = None
    if materiale_ids_csv and materiale_ids_csv.strip():
        try:
            mat_ids = [int(x.strip()) for x in materiale_ids_csv.split(",") if x.strip()]
            if len(mat_ids) == 1:
                mat_id_singolo = mat_ids[0]
                mat_ids = None
        except ValueError:
            return "Errore: materiale_ids_csv deve contenere ID numerici separati da virgola."
    elif materiale_id and materiale_id > 0:
        mat_id_singolo = materiale_id

    print(f"[DEBUG tool_genera_corso] corso_id_eff={corso_id_eff}, argomento='{argomento}', "
          f"mat_id_singolo={mat_id_singolo}, mat_ids={mat_ids}, studente_id={studente_id}, "
          f"forza_ricerca_keyword={forza_ricerca_keyword}")

    stato_finale = esegui_generazione(
        agente=_get_agente_teorico(),
        corso_id=corso_id_eff,
        argomento_richiesto=argomento,
        docente_id=studente_id,
        is_corso_docente=False,
        materiale_id=mat_id_singolo,
        materiale_ids=mat_ids,
        forza_keyword=bool(forza_ricerca_keyword),
    )

    if stato_finale.get("errore"):
        errore = stato_finale["errore"]
        print(f"[DEBUG tool_genera_corso] ERRORE: {errore}")

        # Gestione speciale: ricerca semantica fallita → chiedi consenso all'utente
        if errore.startswith("RICERCA_SEMANTICA_FALLITA|"):
            motivo = errore.split("|", 1)[1]
            return (
                f"La ricerca nel database vettoriale non è riuscita.\n"
                f"Motivo: {motivo}\n\n"
                f"È disponibile una ricerca alternativa basata su parole chiave "
                f"(keyword matching sui metadati), che potrebbe essere meno precisa "
                f"rispetto alla ricerca semantica.\n\n"
                f"Chiedi all'utente se desidera procedere con la ricerca per parole chiave. "
                f"Se l'utente acconsente, richiama questo stesso tool con gli stessi parametri "
                f"ma con forza_ricerca_keyword=1."
            )

        return f"Errore durante la generazione: {errore}"

    print(f"[DEBUG tool_genera_corso] Generazione completata con successo, "
          f"n_chunks={len(stato_finale.get('chunks_recuperati', []))}")

    struttura = stato_finale.get("struttura_corso_generata", {})
    titolo = struttura.get("titolo_corso", "Senza Titolo")

    # Recupera gli ID reali dei paragrafi per la memoria dell'agente
    query_piano = (
        "SELECT id FROM piani_personalizzati "
        "WHERE studente_id = ? ORDER BY id DESC LIMIT 1"
    )
    piani = db.esegui(query_piano, [studente_id])
    if not piani:
        return f"Corso '{titolo}' generato, ma impossibile recuperare le sezioni dal DB."

    piano_id = piani[0]["id"]
    paragrafi = db.esegui(
        """SELECT pp.id, pp.titolo
           FROM piano_paragrafi pp
           JOIN piano_capitoli pc ON pp.capitolo_id = pc.id
           WHERE pc.piano_id = ?""",
        [piano_id],
    )

    # Salva i paragrafi nel contesto di sessione per le richieste successive
    contesto = st.session_state.get(_SK_CONTESTO, {})
    contesto["ultimi_paragrafi"] = paragrafi
    st.session_state[_SK_CONTESTO] = contesto

    elenco = "\n".join(f"- ID {p['id']}: {p['titolo']}" for p in paragrafi)
    return (
        f"SUCCESSO: Corso '{titolo}' generato e salvato.\n"
        f"MEMORIA (usa questi ID per quiz/flashcard se richiesti):\n{elenco}\n"
        f"Suggerisci all'utente di esercitarsi con quiz o flashcard."
    )


@tool
def tool_analizza_coerenza_materiali(materiale_ids_csv: str) -> str:
    """
    Analizza la coerenza tematica tra più materiali didattici selezionati.
    Utile per capire come raggruppare materiali per argomento o per decidere
    come integrare contenuti di più materiali in un piano esistente.

    Parametro materiale_ids_csv: stringa di ID materiali separati da virgola (es. "12,34,56").

    Restituisce un'analisi JSON con:
    - coerenti: true/false — se i materiali trattano lo stesso ambito tematico
    - gruppi: raggruppamento dei materiali per area tematica (se non coerenti)
    - suggerimento: messaggio per l'utente
    """
    if not materiale_ids_csv or not materiale_ids_csv.strip():
        return "Errore: specifica gli ID dei materiali separati da virgola."

    try:
        mat_ids = [int(x.strip()) for x in materiale_ids_csv.split(",") if x.strip()]
    except ValueError:
        return "Errore: materiale_ids_csv deve contenere ID numerici separati da virgola."

    if len(mat_ids) < 2:
        return json.dumps({
            "coerenti": True,
            "motivo": "Un solo materiale selezionato, non serve analisi di coerenza.",
            "materiali": mat_ids,
        }, ensure_ascii=False)

    # Recupera sommari e argomenti chiave di ogni materiale
    sommari = recupera_sommari_materiali(mat_ids)
    if not sommari:
        return "Errore: nessun materiale trovato con gli ID specificati."

    # Costruisci il prompt per l'LLM
    descrizione_materiali = []
    for s in sommari:
        argomenti_str = ", ".join(s["argomenti_chiave"][:15]) if s["argomenti_chiave"] else "(nessun argomento estratto)"
        sommari_str = " | ".join(s["sommari_chunks"][:3]) if s["sommari_chunks"] else "(nessun sommario)"
        descrizione_materiali.append(
            f"- Materiale ID {s['materiale_id']}: \"{s['titolo']}\" (tipo: {s['tipo']})\n"
            f"  Argomenti chiave: {argomenti_str}\n"
            f"  Sommari: {sommari_str}"
        )

    prompt = f"""Analizza i seguenti materiali didattici e determina se sono tematicamente coerenti
(cioè se trattano la stessa materia o argomenti strettamente correlati che possono essere
raggruppati per area tematica).

MATERIALI SELEZIONATI:
{chr(10).join(descrizione_materiali)}

Rispondi ESCLUSIVAMENTE con un JSON valido (senza markdown, senza backtick) con questa struttura:
{{
  "coerenti": true/false,
  "motivo": "spiegazione breve del perché sono o non sono coerenti",
  "gruppi": [
    {{
      "tema": "nome del tema comune",
      "materiale_ids": [lista di ID che appartengono a questo tema],
      "titoli": [lista dei titoli corrispondenti]
    }}
  ]
}}

Se coerenti=true, ci sarà UN solo gruppo con tutti i materiali.
Se coerenti=false, ci saranno più gruppi, uno per ogni area tematica distinta.

Sii ragionevole: materiali di aree vicine (es. due argomenti di informatica) sono coerenti.
Materiali molto diversi (es. marketing e cybersecurity) NON sono coerenti."""

    try:
        llm = get_llm(max_tokens=1024)
        from langchain_core.messages import HumanMessage
        risposta = llm.invoke([HumanMessage(content=prompt)])
        contenuto = risposta.content.strip()
        # Pulizia eventuale markdown
        if contenuto.startswith("```"):
            contenuto = contenuto.split("\n", 1)[1] if "\n" in contenuto else contenuto[3:]
            if contenuto.endswith("```"):
                contenuto = contenuto[:-3]
            contenuto = contenuto.strip()
        # Valida il JSON
        analisi = json.loads(contenuto)
        return json.dumps(analisi, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({
            "coerenti": True,
            "motivo": "Impossibile determinare la coerenza con certezza. Procedo assumendo coerenza.",
            "gruppi": [{"tema": "Tutti i materiali", "materiale_ids": mat_ids, "titoli": [s["titolo"] for s in sommari]}],
        }, ensure_ascii=False)
    except Exception as e:
        return f"Errore durante l'analisi di coerenza: {e}"


@tool
def tool_genera_corso_libero(argomento: str, istruzioni_utente: str = "", forza_ricerca_keyword: int = 0) -> str:
    """
    Genera una lezione attingendo da TUTTI i materiali della piattaforma (modalità 'Lea sceglie').
    Usa questo tool SOLO dopo aver chiarito le intenzioni dello studente (max 3 messaggi).

    Il piano generato include automaticamente un capitolo "Riferimenti bibliografici"
    con l'elenco dei materiali didattici utilizzati come fonte.

    Parametro argomento: topic specifico su cui generare la lezione (non generico).
    Parametro istruzioni_utente: istruzioni aggiuntive raccolte durante la conversazione
    (es. livello di approfondimento, aree da includere/escludere).
    Parametro forza_ricerca_keyword: usa 1 SOLO se la ricerca semantica è fallita
    e l'utente ha dato il consenso esplicito a procedere con la ricerca per parole chiave
    (meno precisa). Default 0.
    """
    studente_id = _STUDENTE_ID_CORRENTE

    # Verifica che ci siano materiali sulla piattaforma
    n_totali = conta_chunk_piattaforma()
    if n_totali == 0:
        return (
            "Nessun materiale didattico disponibile sulla piattaforma. "
            "Non è possibile generare una lezione senza materiale di riferimento."
        )

    # Ricerca platform-wide
    risultato_rag = cerca_chunk_piattaforma(
        query=argomento, top_k=16, forza_keyword=bool(forza_ricerca_keyword),
    )

    # Se la ricerca semantica è fallita, chiedi consenso all'utente
    if risultato_rag.errore_semantico and not forza_ricerca_keyword:
        return (
            f"La ricerca nel database vettoriale non è riuscita.\n"
            f"Motivo: {risultato_rag.errore_semantico}\n\n"
            f"È disponibile una ricerca alternativa basata su parole chiave "
            f"(keyword matching sui metadati), che potrebbe essere meno precisa "
            f"rispetto alla ricerca semantica.\n\n"
            f"Chiedi all'utente se desidera procedere con la ricerca per parole chiave. "
            f"Se l'utente acconsente, richiama questo stesso tool con gli stessi parametri "
            f"ma con forza_ricerca_keyword=1."
        )

    chunks = risultato_rag.chunks
    if not chunks:
        return (
            "Non ho trovato materiale pertinente sull'argomento richiesto. "
            "Prova a riformulare con termini più specifici o scegli un altro argomento."
        )

    # Log info sui materiali coinvolti
    materiale_ids_unici = list({c["materiale_id"] for c in chunks if c.get("materiale_id")})

    print(f"[DEBUG tool_genera_corso_libero] argomento='{argomento}', "
          f"chunks_trovati={len(chunks)}, materiali_coinvolti={len(materiale_ids_unici)}, "
          f"studente_id={studente_id}")

    # Genera il piano usando i chunk già recuperati dalla ricerca platform-wide.
    # Passa i chunk direttamente (chunks_precaricati) per evitare che il nodo RAG
    # ri-cerchi su tutti i materiale_ids e includa materiali non pertinenti.
    stato_finale = esegui_generazione(
        agente=_get_agente_teorico(),
        corso_id=None,
        argomento_richiesto=argomento,
        docente_id=studente_id,
        is_corso_docente=False,
        materiale_id=None,
        materiale_ids=None,
        istruzioni_utente=istruzioni_utente,
        chunks_precaricati=chunks,
    )

    if stato_finale.get("errore"):
        print(f"[DEBUG tool_genera_corso_libero] ERRORE: {stato_finale['errore']}")
        return f"Errore durante la generazione: {stato_finale['errore']}"

    struttura = stato_finale.get("struttura_corso_generata", {})
    titolo = struttura.get("titolo_corso", "Senza Titolo")

    # Recupera il piano_id appena creato
    piani = db.esegui(
        "SELECT id FROM piani_personalizzati "
        "WHERE studente_id = ? ORDER BY id DESC LIMIT 1",
        [studente_id],
    )
    if not piani:
        return f"Lezione '{titolo}' generata, ma impossibile recuperare il piano dal DB."

    piano_id = piani[0]["id"]

    # Assicura che il tipo sia 'libero' (backup nel caso content_gen non lo abbia impostato)
    try:
        db.aggiorna("piani_personalizzati", {"id": piano_id}, {"tipo": "libero"})
    except Exception:
        pass

    # Aggiunge capitolo "Riferimenti bibliografici" con le fonti usate
    try:
        ref_text = formatta_riferimenti_materiali(chunks)

        # Trova l'ordine massimo dei capitoli esistenti
        capitoli_esistenti = db.esegui(
            "SELECT MAX(ordine) AS max_ord FROM piano_capitoli WHERE piano_id = ?",
            [piano_id],
        )
        ordine_ref = (capitoli_esistenti[0]["max_ord"] or 0) + 1 if capitoli_esistenti else 999

        cap_ref_id = db.inserisci("piano_capitoli", {
            "piano_id": piano_id,
            "titolo": "Riferimenti bibliografici",
            "ordine": ordine_ref,
        })
        par_ref_id = db.inserisci("piano_paragrafi", {
            "capitolo_id": cap_ref_id,
            "titolo": "Elenco fonti",
            "ordine": 0,
        })
        db.inserisci("piano_contenuti", {
            "paragrafo_id": par_ref_id,
            "tipo": "lezione",
            "contenuto_json": ref_text,
            "chunk_ids_utilizzati": json.dumps([c["id"] for c in chunks]),
        })
    except Exception as e:
        print(f"[DEBUG tool_genera_corso_libero] Errore aggiunta riferimenti: {e}")

    # Recupera i paragrafi generati per la memoria dell'agente
    paragrafi = db.esegui(
        """SELECT pp.id, pp.titolo
           FROM piano_paragrafi pp
           JOIN piano_capitoli pc ON pp.capitolo_id = pc.id
           WHERE pc.piano_id = ?""",
        [piano_id],
    )

    # Aggiorna contesto sessione
    try:
        contesto = st.session_state.get(_SK_CONTESTO, {})
        contesto["ultimi_paragrafi"] = paragrafi
        st.session_state[_SK_CONTESTO] = contesto
    except Exception:
        pass

    # Nomi dei materiali usati per il messaggio di ritorno
    nomi_materiali = []
    for mid in materiale_ids_unici:
        info = db.esegui("SELECT titolo FROM materiali_didattici WHERE id = ?", [mid])
        if info:
            nomi_materiali.append(info[0]["titolo"])

    elenco = "\n".join(f"- ID {p['id']}: {p['titolo']}" for p in paragrafi)
    fonti = "\n".join(f"- {n}" for n in nomi_materiali) if nomi_materiali else "(nessuna fonte specifica)"

    return (
        f"SUCCESSO: Lezione '{titolo}' generata dalla piattaforma e salvata come piano libero.\n"
        f"Materiali della piattaforma utilizzati:\n{fonti}\n\n"
        f"MEMORIA (usa questi ID per quiz/flashcard se richiesti):\n{elenco}\n"
        f"Il piano include un capitolo 'Riferimenti bibliografici' con le fonti.\n"
        f"Suggerisci all'utente di consultare il piano e di esercitarsi con quiz o flashcard."
    )


@tool
def tool_rispondi_domanda(domanda: str, contesto_aggiuntivo: str = "") -> str:
    """
    Rispondi a una domanda dello studente su un argomento, concetto o contenuto
    del corso/piano, SENZA generare un piano o una lezione completa.

    Usa questo tool quando lo studente:
    - Chiede una spiegazione su un argomento (es. "Parlami del Deep Learning")
    - Vuole capire meglio un concetto (es. "Spiegami le reti neurali")
    - Chiede di riassumere un capitolo o paragrafo
    - Ha un dubbio su qualcosa che sta studiando
    - Chiede esempi su un argomento
    - Fa domande di tipo "cos'è", "come funziona", "perché", "qual è la differenza tra..."

    NON usare questo tool per generare piani di studio, quiz o flashcard.

    Parametro domanda: la domanda o richiesta dello studente.
    Parametro contesto_aggiuntivo: eventuale contesto extra (es. nome del paragrafo,
    capitolo specifico, testo da approfondire). Se lo studente fa riferimento a un
    paragrafo o capitolo specifico del piano, includi qui il titolo.
    """
    studente_id = _STUDENTE_ID_CORRENTE
    contesto = _CONTESTO_CORRENTE

    # --- 1. Raccogli contesto dal piano personalizzato (se attivo) ---
    contenuto_piano = ""
    if contesto.get("piano_id"):
        piano_id = contesto["piano_id"]
        # Se c'è un riferimento a un paragrafo/capitolo specifico nel contesto_aggiuntivo,
        # cerca il contenuto di quel paragrafo
        if contesto_aggiuntivo:
            # Cerca paragrafi il cui titolo corrisponde parzialmente
            paragrafi = db.esegui(
                """SELECT pp.id, pp.titolo, pc.contenuto_json
                   FROM piano_paragrafi pp
                   JOIN piano_capitoli cap ON pp.capitolo_id = cap.id
                   LEFT JOIN piano_contenuti pc ON pc.paragrafo_id = pp.id AND pc.tipo = 'lezione'
                   WHERE cap.piano_id = ?""",
                [piano_id],
            )
            # Cerca anche i capitoli
            capitoli = db.esegui(
                "SELECT id, titolo FROM piano_capitoli WHERE piano_id = ? ORDER BY ordine",
                [piano_id],
            )

            contesto_lower = contesto_aggiuntivo.lower()
            parti_piano = []

            # Match su capitoli
            for cap in capitoli:
                if cap["titolo"].lower() in contesto_lower or contesto_lower in cap["titolo"].lower():
                    # Recupera tutti i paragrafi di questo capitolo
                    par_cap = db.esegui(
                        """SELECT pp.titolo, pc.contenuto_json
                           FROM piano_paragrafi pp
                           LEFT JOIN piano_contenuti pc ON pc.paragrafo_id = pp.id AND pc.tipo = 'lezione'
                           WHERE pp.capitolo_id = ? ORDER BY pp.ordine""",
                        [cap["id"]],
                    )
                    for p in par_cap:
                        if p.get("contenuto_json"):
                            parti_piano.append(f"### {p['titolo']}\n{p['contenuto_json'][:3000]}")

            # Match su paragrafi
            for par in paragrafi:
                if par["titolo"].lower() in contesto_lower or contesto_lower in par["titolo"].lower():
                    if par.get("contenuto_json"):
                        parti_piano.append(f"### {par['titolo']}\n{par['contenuto_json'][:5000]}")

            if parti_piano:
                contenuto_piano = "\n\n".join(parti_piano[:3])  # max 3 sezioni

        # Se non c'è match specifico, prendi un sommario del piano
        if not contenuto_piano:
            paragrafi_piano = db.esegui(
                """SELECT pp.titolo, SUBSTR(pc.contenuto_json, 1, 500) AS anteprima
                   FROM piano_paragrafi pp
                   JOIN piano_capitoli cap ON pp.capitolo_id = cap.id
                   LEFT JOIN piano_contenuti pc ON pc.paragrafo_id = pp.id AND pc.tipo = 'lezione'
                   WHERE cap.piano_id = ? ORDER BY cap.ordine, pp.ordine""",
                [piano_id],
            )
            if paragrafi_piano:
                sommario_parti = []
                for p in paragrafi_piano[:8]:
                    anteprima = (p.get("anteprima") or "(non ancora generato)")[:300]
                    sommario_parti.append(f"- {p['titolo']}: {anteprima}")
                contenuto_piano = "Sommario del piano attivo:\n" + "\n".join(sommario_parti)

    # --- 2. Cerca materiale rilevante con RAG ---
    contesto_rag = ""
    corso_id = contesto.get("corso_id")
    doc_chat = contesto.get("documento_chat")
    mat_sel = contesto.get("materiale_selezionato")

    # Costruisci la query di ricerca combinando domanda e contesto
    query_ricerca = domanda
    if contesto_aggiuntivo:
        query_ricerca = f"{domanda} {contesto_aggiuntivo}"

    try:
        if doc_chat or mat_sel:
            # Modalità chat documento o materiale selezionato: cerca SOLO in quel documento
            mat_id = (doc_chat or mat_sel)["id"]
            mat_corso_id = (doc_chat or mat_sel).get("corso_id")
            risultato = cerca_chunk_rilevanti(
                mat_corso_id, query_ricerca, top_k=8,
                materiale_id=mat_id,
            )
        elif corso_id:
            # Cerca nel corso specifico
            risultato = cerca_chunk_rilevanti(corso_id, query_ricerca, top_k=6)
        else:
            # Cerca su tutta la piattaforma
            risultato = cerca_chunk_piattaforma(query_ricerca, top_k=6)

        if risultato.chunks:
            contesto_rag = formatta_contesto_rag(risultato.chunks)
    except Exception as e:
        print(f"[DEBUG tool_rispondi_domanda] Errore RAG: {e}")

    # --- 3. Costruisci il prompt per la risposta ---
    parti_contesto = []
    if contenuto_piano:
        parti_contesto.append(f"CONTENUTO DAL PIANO PERSONALIZZATO DELLO STUDENTE:\n{contenuto_piano}")
    if contesto_rag:
        parti_contesto.append(f"MATERIALE DIDATTICO RILEVANTE (da RAG):\n{contesto_rag}")

    contesto_completo = "\n\n---\n\n".join(parti_contesto) if parti_contesto else "(Nessun materiale specifico trovato)"

    corso_nome = contesto.get("corso_nome", "")
    piano_titolo = contesto.get("piano_titolo", "")
    info_contesto = ""
    if doc_chat:
        info_contesto += f"MODALITÀ CHAT DOCUMENTO: lo studente sta chattando sul documento '{doc_chat['titolo']}'. "
    if corso_nome:
        info_contesto += f"Corso attivo: {corso_nome}. "
    if piano_titolo:
        info_contesto += f"Piano attivo: {piano_titolo}. "

    # Istruzioni specifiche per modalità documento
    if doc_chat:
        istruzioni_extra = (
            "- Lo studente sta chattando su un DOCUMENTO SPECIFICO. Basa la risposta "
            "PRINCIPALMENTE sul contenuto del documento fornito.\n"
            "- Se la domanda riguarda qualcosa che il documento non tratta, segnalalo "
            "chiaramente e rispondi con le tue conoscenze generali indicando che stai "
            "integrando oltre il contenuto del documento.\n"
            "- Quando citi informazioni dal documento, indicalo naturalmente "
            "(es. 'Come descritto nel documento...', 'Il materiale spiega che...').\n"
            "- NON proporre di creare piani o lezioni: lo studente vuole chattare sul documento."
        )
    else:
        istruzioni_extra = (
            "- Se il materiale disponibile copre l'argomento, basa la risposta su di esso "
            "citando i concetti chiave.\n"
            "- Se il materiale non copre completamente l'argomento, integra con le tue "
            "conoscenze generali ma segnala chiaramente cosa viene dal materiale del corso "
            "e cosa è una tua integrazione.\n"
            "- NON proporre di creare piani o lezioni: lo studente vuole una risposta diretta."
        )

    prompt = f"""Sei Lea, tutor didattico della piattaforma LearnAI. Rispondi alla domanda dello
studente in modo chiaro, esaustivo e coinvolgente, basandoti sul materiale didattico disponibile.

{info_contesto}

DOMANDA DELLO STUDENTE:
{domanda}

{f"CONTESTO AGGIUNTIVO: {contesto_aggiuntivo}" if contesto_aggiuntivo else ""}

MATERIALE DI RIFERIMENTO:
{contesto_completo}

ISTRUZIONI PER LA RISPOSTA:
- Rispondi in italiano con tono caldo e motivante.
- Spiega in modo chiaro, usando esempi concreti quando possibile.
{istruzioni_extra}
- Se appropriato, alla fine suggerisci domande di approfondimento o argomenti correlati.
- Usa formattazione Markdown (grassetto, elenchi, titoli) per rendere la risposta leggibile.
- Se lo studente chiede un riassunto, sii sintetico ma completo sui punti chiave.
- Se lo studente chiede esempi, fornisci esempi pratici e concreti."""

    try:
        llm = get_llm(max_tokens=4096)
        from langchain_core.messages import HumanMessage as HM
        risposta = llm.invoke([HM(content=prompt)])
        return risposta.content
    except Exception as e:
        return f"Mi dispiace, ho avuto un problema nel rispondere alla tua domanda: {e}"


@tool
def tool_genera_pratica(paragrafo_id: int, strumenti: list[str]) -> str:
    """
    Genera strumenti pratici (quiz, flashcard, schema) per una sezione studiata.
    strumenti: lista con uno o più tra "quiz", "flashcard", "schema".
    IMPORTANTE: quiz e flashcard possono essere generati SOLO per sezioni di un
    piano personalizzato dello studente. Se lo studente non ha piani, suggerisci
    di crearne uno prima.
    """
    studente_id = _STUDENTE_ID_CORRENTE

    # Verifica che il paragrafo appartenga a un piano dello studente
    verifica = db.esegui(
        "SELECT pp.id FROM piano_paragrafi pp "
        "JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
        "JOIN piani_personalizzati p ON pc.piano_id = p.id "
        "WHERE pp.id = ? AND p.studente_id = ?",
        [paragrafo_id, studente_id],
    )
    if not verifica:
        # Controlla se lo studente ha almeno un piano
        piani = db.esegui(
            "SELECT id, titolo FROM piani_personalizzati "
            "WHERE studente_id = ? AND stato = 'attivo'",
            [studente_id],
        )
        if not piani:
            return (
                "Non puoi generare quiz o flashcard perché non hai ancora nessun piano personalizzato. "
                "Crea prima un piano personalizzato sull'argomento che ti interessa, "
                "poi potrai generare quiz e flashcard per le sue sezioni."
            )
        elenco = ", ".join(f"'{p['titolo']}'" for p in piani)
        return (
            f"La sezione indicata non appartiene a un tuo piano personalizzato. "
            f"Quiz e flashcard possono essere generati solo per sezioni di un tuo piano. "
            f"I tuoi piani attivi sono: {elenco}. "
            f"Indica a quale piano vuoi associare quiz o flashcard."
        )

    contenuti = db.trova_tutti(
        "piano_contenuti", {"paragrafo_id": paragrafo_id, "tipo": "lezione"}
    )
    if not contenuti or not contenuti[0].get("contenuto_json"):
        return f"Nessun testo trovato per la sezione ID {paragrafo_id}. Genera prima il corso teorico."

    testo_paragrafo = contenuti[0]["contenuto_json"]
    try:
        chunk_ids = json.loads(contenuti[0].get("chunk_ids_utilizzati", "[]"))
    except (json.JSONDecodeError, TypeError):
        chunk_ids = []

    stato_finale = esegui_generazione_pratica(
        paragrafo_id=paragrafo_id,
        testo_paragrafo=testo_paragrafo,
        strumenti_richiesti=strumenti,
        studente_id=studente_id,
        chunk_ids_utilizzati=chunk_ids,
    )

    if stato_finale.get("errore"):
        return f"Errore nella generazione pratica: {stato_finale['errore']}"

    generati = list(stato_finale.get("strumenti_generati", {}).keys())
    nomi = {"quiz": "Quiz", "flashcards": "Flashcard", "schema_mermaid": "Schema concettuale"}
    leggibili = [nomi.get(g, g) for g in generati]

    return f"SUCCESSO: {' e '.join(leggibili)} generati e salvati per la sezione {paragrafo_id}."


@tool
def tool_analizza_preparazione(tentativo_id: int) -> str:
    """
    Analizza le risposte errate di un tentativo quiz e identifica le lacune dello studente.
    Fornisce consigli su cosa rivedere e può proporre di ottimizzare il piano di studio.
    Usa questo tool quando lo studente chiede di analizzare i risultati di un quiz o
    vuole capire cosa migliorare dopo aver completato un questionario.
    """
    studente_id = _STUDENTE_ID_CORRENTE
    try:
        return analizza_gap(tentativo_id, studente_id)
    except Exception as e:
        return f"Errore durante l'analisi delle lacune: {e}"


@tool
def tool_modifica_piano(piano_id: int, azione: str, target_id: int, nuovo_valore: str = "", materiale_id: int = 0) -> str:
    """
    Modifica la struttura o il contenuto di un piano (studente o corso docente).

    azione può essere:
      - 'rinomina_capitolo'       → rinomina piano_capitoli.titolo (target_id = capitolo_id)
      - 'rinomina_paragrafo'      → rinomina piano_paragrafi.titolo (target_id = paragrafo_id)
      - 'riordina_capitolo'       → sposta il capitolo in una nuova posizione (nuovo_valore = intero)
      - 'riordina_paragrafo'      → sposta il paragrafo in una nuova posizione (nuovo_valore = intero)
      - 'elimina_capitolo'        → elimina il capitolo e tutti i suoi paragrafi (target_id = capitolo_id)
      - 'elimina_paragrafo'       → elimina il paragrafo e i suoi contenuti (target_id = paragrafo_id)
      - 'aggiungi_capitolo'       → aggiunge un nuovo capitolo al piano (nuovo_valore = titolo)
      - 'aggiungi_paragrafo'      → aggiunge un nuovo paragrafo a un capitolo (target_id = capitolo_id,
                                    nuovo_valore = titolo del paragrafo). Restituisce l'ID del paragrafo
                                    creato, che puoi usare con 'riscrivi_contenuto' per scrivere il testo.
      - 'sposta_paragrafo'        → sposta il paragrafo in un altro capitolo (target_id = paragrafo_id,
                                    nuovo_valore = capitolo_id di destinazione come stringa intera).
                                    Usalo per riorganizzare paragrafi tra capitoli diversi.
      - 'leggi_contenuto'         → legge il testo attuale di un paragrafo (target_id = paragrafo_id).
                                    Usalo PRIMA di riscrivere, per basare la riscrittura sul testo originale.
      - 'riscrivi_contenuto'      → sostituisce il testo di un paragrafo (target_id = paragrafo_id,
                                    nuovo_valore = testo completo riscritto). Il testo deve essere
                                    completo e ben strutturato, non un riassunto.
                                    materiale_id (opzionale): se il testo è stato arricchito usando un
                                    materiale specifico, passa il materiale_id per tracciarlo nel piano.

    Usa 'leggi_contenuto' + 'riscrivi_contenuto' quando lo studente chiede di riscrivere,
    modificare, semplificare, espandere o tradurre il testo di un paragrafo.
    """
    studente_id = _STUDENTE_ID_CORRENTE

    # Verifica che il piano appartenga allo studente corrente
    piano = db.trova_uno("piani_personalizzati", {"id": piano_id, "studente_id": studente_id})
    if not piano:
        return f"Piano ID {piano_id} non trovato o non appartiene allo studente corrente."

    try:
        if azione == "rinomina_capitolo":
            if not nuovo_valore:
                return "Specifica il nuovo titolo per il capitolo."
            db.aggiorna("piano_capitoli", {"id": target_id, "piano_id": piano_id}, {"titolo": nuovo_valore})
            return f"Capitolo rinominato in '{nuovo_valore}'."

        elif azione == "rinomina_paragrafo":
            if not nuovo_valore:
                return "Specifica il nuovo titolo per il paragrafo."
            # Verifica che il paragrafo appartenga al piano
            par = db.esegui(
                "SELECT pp.id FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            db.aggiorna("piano_paragrafi", {"id": target_id}, {"titolo": nuovo_valore})
            return f"Paragrafo rinominato in '{nuovo_valore}'."

        elif azione == "sposta_paragrafo":
            try:
                capitolo_dest_id = int(nuovo_valore)
            except (ValueError, TypeError):
                return "Specifica il capitolo_id di destinazione come numero intero."
            # Verifica che il paragrafo appartenga al piano
            par = db.esegui(
                "SELECT pp.id, pp.titolo FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            # Verifica che il capitolo di destinazione appartenga al piano
            cap_dest = db.trova_uno("piano_capitoli", {"id": capitolo_dest_id, "piano_id": piano_id})
            if not cap_dest:
                return f"Capitolo ID {capitolo_dest_id} non trovato in questo piano."
            db.aggiorna("piano_paragrafi", {"id": target_id}, {"capitolo_id": capitolo_dest_id})
            return f"Paragrafo '{par[0]['titolo']}' spostato nel capitolo '{cap_dest['titolo']}'."

        elif azione == "riordina_capitolo":
            try:
                nuovo_ordine = int(nuovo_valore)
            except (ValueError, TypeError):
                return "Specifica la nuova posizione (numero intero, partendo da 1)."
            db.aggiorna("piano_capitoli", {"id": target_id, "piano_id": piano_id}, {"ordine": nuovo_ordine - 1})
            return f"Capitolo spostato alla posizione {nuovo_ordine}."

        elif azione == "riordina_paragrafo":
            try:
                nuovo_ordine = int(nuovo_valore)
            except (ValueError, TypeError):
                return "Specifica la nuova posizione (numero intero, partendo da 1)."
            par = db.esegui(
                "SELECT pp.id FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            db.aggiorna("piano_paragrafi", {"id": target_id}, {"ordine": nuovo_ordine - 1})
            return f"Paragrafo spostato alla posizione {nuovo_ordine}."

        elif azione == "elimina_capitolo":
            cap = db.trova_uno("piano_capitoli", {"id": target_id, "piano_id": piano_id})
            if not cap:
                return f"Capitolo ID {target_id} non trovato in questo piano."
            titolo = cap.get("titolo", "")
            db.esegui("DELETE FROM piano_capitoli WHERE id = ? AND piano_id = ?", [target_id, piano_id])
            return f"Capitolo '{titolo}' e tutti i suoi contenuti eliminati."

        elif azione == "elimina_paragrafo":
            par = db.esegui(
                "SELECT pp.id, pp.titolo FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            titolo = par[0].get("titolo", "")
            db.esegui("DELETE FROM piano_paragrafi WHERE id = ?", [target_id])
            return f"Paragrafo '{titolo}' e i suoi contenuti eliminati."

        elif azione == "aggiungi_capitolo":
            if not nuovo_valore:
                return "Specifica il titolo per il nuovo capitolo."
            # Trova l'ordine massimo attuale
            capitoli = db.trova_tutti("piano_capitoli", {"piano_id": piano_id}, ordine="ordine DESC", limite=1)
            nuovo_ordine = (capitoli[0]["ordine"] + 1) if capitoli else 0
            nuovo_id = db.inserisci("piano_capitoli", {
                "piano_id": piano_id,
                "titolo": nuovo_valore,
                "ordine": nuovo_ordine,
                "completato": 0,
            })
            return f"Nuovo capitolo '{nuovo_valore}' aggiunto al piano (ID: {nuovo_id})."

        elif azione == "aggiungi_paragrafo":
            if not nuovo_valore:
                return "Specifica il titolo per il nuovo paragrafo."
            # target_id = capitolo_id a cui aggiungere il paragrafo
            cap = db.trova_uno("piano_capitoli", {"id": target_id, "piano_id": piano_id})
            if not cap:
                return f"Capitolo ID {target_id} non trovato in questo piano."
            paragrafi = db.trova_tutti("piano_paragrafi", {"capitolo_id": target_id}, ordine="ordine DESC", limite=1)
            nuovo_ordine = (paragrafi[0]["ordine"] + 1) if paragrafi else 0
            nuovo_id = db.inserisci("piano_paragrafi", {
                "capitolo_id": target_id,
                "titolo": nuovo_valore,
                "ordine": nuovo_ordine,
            })
            return f"Nuovo paragrafo '{nuovo_valore}' aggiunto al capitolo '{cap['titolo']}' (paragrafo ID: {nuovo_id}). Usa 'riscrivi_contenuto' con target_id={nuovo_id} per scrivere il testo."

        elif azione == "leggi_contenuto":
            # Verifica che il paragrafo appartenga al piano
            par = db.esegui(
                "SELECT pp.titolo FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            contenuto = db.trova_uno("piano_contenuti", {"paragrafo_id": target_id, "tipo": "lezione"})
            if not contenuto or not contenuto.get("contenuto_json"):
                return f"Nessun testo trovato per '{par[0]['titolo']}'. Il paragrafo potrebbe non avere ancora una lezione generata."
            return (
                f"TESTO ATTUALE del paragrafo '{par[0]['titolo']}':\n\n"
                f"{contenuto['contenuto_json']}\n\n"
                f"Ora genera una versione migliorata e salvala con 'riscrivi_contenuto'."
            )

        elif azione == "riscrivi_contenuto":
            if not nuovo_valore or not nuovo_valore.strip():
                return "Specifica il nuovo testo completo per il paragrafo."
            par = db.esegui(
                "SELECT pp.titolo FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id "
                "WHERE pp.id = ? AND pc.piano_id = ?",
                [target_id, piano_id],
            )
            if not par:
                return f"Paragrafo ID {target_id} non trovato in questo piano."
            titolo = par[0]["titolo"]
            # Aggiorna se esiste, altrimenti inserisce
            esistente = db.trova_uno("piano_contenuti", {"paragrafo_id": target_id, "tipo": "lezione"})
            if esistente:
                aggiornamento = {"contenuto_json": nuovo_valore.strip()}
                # Se è stato usato un materiale, aggiungi i suoi chunk_ids a quelli esistenti
                if materiale_id and materiale_id > 0:
                    chunk_ids_esistenti: list = []
                    try:
                        chunk_ids_esistenti = json.loads(esistente.get("chunk_ids_utilizzati") or "[]")
                    except (json.JSONDecodeError, TypeError):
                        pass
                    nuovi_chunks = db.esegui(
                        "SELECT id FROM materiali_chunks WHERE materiale_id = ?",
                        [materiale_id],
                    )
                    for c in nuovi_chunks:
                        if c["id"] not in chunk_ids_esistenti:
                            chunk_ids_esistenti.append(c["id"])
                    aggiornamento["chunk_ids_utilizzati"] = json.dumps(chunk_ids_esistenti)
                db.aggiorna(
                    "piano_contenuti",
                    {"paragrafo_id": target_id, "tipo": "lezione"},
                    aggiornamento,
                )
            else:
                nuovo_record = {
                    "paragrafo_id": target_id,
                    "tipo": "lezione",
                    "contenuto_json": nuovo_valore.strip(),
                }
                if materiale_id and materiale_id > 0:
                    nuovi_chunks = db.esegui(
                        "SELECT id FROM materiali_chunks WHERE materiale_id = ?",
                        [materiale_id],
                    )
                    nuovo_record["chunk_ids_utilizzati"] = json.dumps([c["id"] for c in nuovi_chunks])
                db.inserisci("piano_contenuti", nuovo_record)
            return f"✅ Paragrafo '{titolo}' riscritto e salvato nel piano. Lo studente vedrà la nuova versione al prossimo caricamento."

        else:
            return f"Azione '{azione}' non riconosciuta. Azioni valide: rinomina_capitolo, rinomina_paragrafo, riordina_capitolo, riordina_paragrafo, elimina_capitolo, elimina_paragrafo, aggiungi_capitolo, aggiungi_paragrafo, sposta_paragrafo, leggi_contenuto, riscrivi_contenuto."

    except Exception as e:
        return f"Errore durante la modifica del piano: {e}"


@tool
def tool_analizza_classe(corso_universitario_id: int = None) -> str:
    """
    Analizza le performance della classe per un docente: punteggio medio, tasso di superamento,
    argomenti con più errori, studenti a rischio. Usa questo tool quando il docente chiede
    di analizzare le risposte degli studenti, l'andamento del corso o chi è in difficoltà.
    Se corso_universitario_id è 0 o None, analizza tutti i corsi del docente.
    """
    docente_id = _STUDENTE_ID_CORRENTE  # in modalità docente, questo è il docente_id

    filtro = ""
    params: list = [docente_id]
    if corso_universitario_id:
        filtro = " AND cu.id = ?"
        params.append(corso_universitario_id)

    # Verifica che esistano tentativi
    riga_media = db.esegui(
        "SELECT AVG(t.punteggio) AS media, "
        "COUNT(CASE WHEN t.punteggio >= 60 THEN 1 END) * 100.0 / MAX(COUNT(*), 1) AS tasso, "
        "COUNT(t.id) AS tentativi, COUNT(DISTINCT t.studente_id) AS studenti "
        "FROM tentativi_quiz t "
        "JOIN quiz q ON q.id = t.quiz_id "
        "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
        "WHERE cu.docente_id = ?" + filtro,
        params,
    )

    if not riga_media or not riga_media[0].get("tentativi"):
        return (
            "Nessun tentativo quiz registrato per i tuoi corsi ancora. "
            "Gli studenti devono completare almeno un quiz perché i dati appaiano qui."
        )

    r = riga_media[0]
    media = round(r["media"] or 0, 1)
    tasso = round(r["tasso"] or 0, 1)
    tentativi = r["tentativi"]
    studenti = r["studenti"]

    risultato = [
        "📊 ANALISI DELLA CLASSE:",
        f"- Studenti coinvolti: {studenti}",
        f"- Tentativi quiz totali: {tentativi}",
        f"- Punteggio medio: {media}/100",
        f"- Tasso superamento (≥60): {tasso}%",
    ]

    # Argomenti più difficili (richiede chunk collegati ai quiz)
    righe_gap = db.esegui(
        "SELECT mc.argomenti_chiave "
        "FROM risposte_domande rd "
        "JOIN domande_quiz dq ON rd.domanda_id = dq.id "
        "JOIN materiali_chunks mc ON dq.chunk_id = mc.id "
        "JOIN quiz q ON dq.quiz_id = q.id "
        "JOIN corsi_universitari cu ON q.corso_universitario_id = cu.id "
        "WHERE cu.docente_id = ? AND rd.corretta = 0 AND mc.argomenti_chiave IS NOT NULL"
        + filtro,
        params,
    )
    conteggio: dict = {}
    for row in righe_gap:
        try:
            for arg in json.loads(row["argomenti_chiave"]):
                conteggio[arg] = conteggio.get(arg, 0) + 1
        except Exception:
            pass
    if conteggio:
        top = sorted(conteggio.items(), key=lambda x: x[1], reverse=True)[:5]
        risultato.append("\n🔴 Argomenti con più errori:")
        for arg, cnt in top:
            risultato.append(f"  - {arg}: {cnt} errori")

    # Domande più sbagliate
    righe_dom = db.esegui(
        "SELECT dq.testo, "
        "ROUND(SUM(CASE WHEN rd.corretta=0 THEN 1 ELSE 0 END)*100.0/COUNT(*),0) AS pct_errore "
        "FROM risposte_domande rd "
        "JOIN domande_quiz dq ON rd.domanda_id = dq.id "
        "JOIN quiz q ON dq.quiz_id = q.id "
        "JOIN corsi_universitari cu ON q.corso_universitario_id = cu.id "
        "WHERE cu.docente_id = ?" + filtro +
        " GROUP BY dq.id HAVING SUM(CASE WHEN rd.corretta=0 THEN 1 ELSE 0 END) > 0"
        " ORDER BY pct_errore DESC LIMIT 3",
        params,
    )
    if righe_dom:
        risultato.append("\n❓ Domande più difficili:")
        for row in righe_dom:
            testo = (row["testo"] or "")[:70] + ("…" if len(row["testo"] or "") > 70 else "")
            risultato.append(f"  - {int(row['pct_errore'] or 0)}% errori — {testo}")

    # Studenti a rischio
    righe_rischio = db.esegui(
        "SELECT u.nome || ' ' || u.cognome AS studente, "
        "ROUND(AVG(t.punteggio),1) AS media, COUNT(t.id) AS n_tentativi "
        "FROM tentativi_quiz t "
        "JOIN quiz q ON q.id = t.quiz_id "
        "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
        "JOIN users u ON u.id = t.studente_id "
        "WHERE cu.docente_id = ?" + filtro +
        " GROUP BY t.studente_id HAVING media < 60 ORDER BY media ASC LIMIT 5",
        params,
    )
    if righe_rischio:
        risultato.append("\n⚠️ Studenti a rischio (media < 60):")
        for row in righe_rischio:
            risultato.append(
                f"  - {row['studente']}: media {row['media']}/100 ({row['n_tentativi']} tentativo/i)"
            )
    else:
        risultato.append("\n✅ Nessuno studente con media sotto il 60% al momento.")

    return "\n".join(risultato)


# ===========================================================================
# Singleton helpers (tutti in session_state)
# ===========================================================================

def _get_agente_teorico():
    """Agente ContentGen: singleton in session_state per sopravvivere ai rerun."""
    if _SK_AGENTE_TEORICO not in st.session_state:
        st.session_state[_SK_AGENTE_TEORICO] = crea_agente_content_gen()
    return st.session_state[_SK_AGENTE_TEORICO]


def _get_orchestratore():
    """Orchestratore: singleton per ruolo in session_state con memoria LangGraph intatta.

    Crea e mantiene due istanze separate — una per studente, una per docente —
    ognuna con prompt e tool set specifici per il ruolo. Il ruolo viene letto da
    session_state.user_role (valorizzato in app.py al login).
    """
    ruolo = (st.session_state.get("user_role") or "").lower()

    if ruolo == "docente":
        if _SK_ORCHESTRATORE_DOCENTE not in st.session_state:
            st.session_state[_SK_ORCHESTRATORE_DOCENTE] = crea_agente(
                tools=[
                    tool_leggi_contesto,
                    tool_esplora_catalogo,
                    tool_genera_corso,
                    tool_genera_pratica,
                    tool_analizza_classe,
                    tool_modifica_piano,
                    tool_analizza_coerenza_materiali,
                ],
                system_prompt=_SYSTEM_PROMPT_DOCENTE,
                memoria=True,
            )
        return st.session_state[_SK_ORCHESTRATORE_DOCENTE]

    # Default: studente
    if _SK_ORCHESTRATORE not in st.session_state:
        st.session_state[_SK_ORCHESTRATORE] = crea_agente(
            tools=[
                tool_leggi_contesto,
                tool_esplora_catalogo,
                tool_genera_corso,
                tool_genera_corso_libero,
                tool_rispondi_domanda,
                tool_genera_pratica,
                tool_analizza_preparazione,
                tool_modifica_piano,
                tool_analizza_coerenza_materiali,
            ],
            system_prompt=_SYSTEM_PROMPT,
            memoria=True,
        )
    return st.session_state[_SK_ORCHESTRATORE]


def _get_thread_id() -> str:
    """Thread ID stabile per sessione utente, usato dal checkpointer di LangGraph.

    Il thread ID include il ruolo per garantire memoria conversazionale separata
    tra le due istanze (studente e docente) dello stesso utente.
    """
    if _SK_THREAD_ID not in st.session_state:
        user_id = st.session_state.get("user", {}).get("user_id", "anonimo")
        ruolo = (st.session_state.get("user_role") or "studente").lower()
        st.session_state[_SK_THREAD_ID] = f"lea_sessione_{ruolo}_{user_id}"
    return st.session_state[_SK_THREAD_ID]


# ===========================================================================
# API pubblica
# ===========================================================================

def aggiorna_contesto_sessione(
    corso_id: int | None = None,
    corso_nome: str | None = None,
    tipo_vista: str | None = None,
    piano_id: int | None = None,
    piano_titolo: str | None = None,
    materiale_selezionato: dict | None = None,
    materiali_selezionati: list[dict] | None = None,
    clear_materiale: bool = False,
    clear_corso: bool = False,
    extra: dict | None = None,
) -> None:
    """Aggiorna il contesto della sessione quando l'utente naviga tra le pagine.

    Chiamare dalle pagine Streamlit ogni volta che l'utente apre un corso o un piano.
    L'agente leggerà questo contesto tramite tool_leggi_contesto.

    Args:
        corso_id:              ID del corso attualmente visualizzato.
        corso_nome:            Nome leggibile del corso.
        tipo_vista:            "docente" | "corso" (sola lettura) | "piano" (piano personalizzato studente).
        piano_id:              ID del piano personalizzato attivo (solo quando tipo_vista="piano").
        piano_titolo:          Titolo del piano attivo.
        materiale_selezionato: Dict {"id", "titolo", "corso_id"} del materiale scelto dallo studente.
        materiali_selezionati: Lista di dict {"id", "titolo", "corso_id"} per selezione multipla.
        clear_materiale:       Se True, rimuove materiale_selezionato dal contesto.
        clear_corso:           Se True, rimuove corso_id e corso_nome dal contesto (es. materiale senza corso).
    """
    global _CONTESTO_CORRENTE
    contesto = st.session_state.get(_SK_CONTESTO, {})

    # Se cambia il tipo_vista (es. da "piano" studente a "docente"), azzera
    # il contesto precedente per evitare contaminazione cross-ruolo.
    if tipo_vista is not None and contesto.get("tipo_vista") != tipo_vista:
        contesto = {"tipo_vista": tipo_vista}
    elif tipo_vista is not None:
        contesto["tipo_vista"] = tipo_vista

    if clear_corso:
        contesto.pop("corso_id", None)
        contesto.pop("corso_nome", None)
        contesto["ultimi_paragrafi"] = []
    elif corso_id is not None:
        contesto["corso_id"] = corso_id
        contesto["ultimi_paragrafi"] = []   # reset sezioni al cambio corso
    if corso_nome is not None:
        contesto["corso_nome"] = corso_nome
    if piano_id is not None:
        contesto["piano_id"] = piano_id
    if piano_titolo is not None:
        contesto["piano_titolo"] = piano_titolo
    if materiale_selezionato is not None:
        contesto["materiale_selezionato"] = materiale_selezionato
    if materiali_selezionati is not None:
        contesto["materiali_selezionati"] = materiali_selezionati
    if clear_materiale:
        contesto.pop("materiale_selezionato", None)
        contesto.pop("materiali_selezionati", None)
        contesto.pop("documento_chat", None)
    if extra:
        contesto.update(extra)
    st.session_state[_SK_CONTESTO] = contesto
    # Copia nel globale: i tool LangGraph girano in thread background dove
    # st.session_state non è accessibile, ma il globale di modulo sì.
    _CONTESTO_CORRENTE = dict(contesto)


def chat_con_orchestratore(
    messaggio_utente: str,
    corso_contestuale_id: int | None = None,
    corso_contestuale_nome: str | None = None,
) -> str:
    """Punto di ingresso unico per le pagine Streamlit.

    Args:
        messaggio_utente:       Testo scritto dall'utente.
        corso_contestuale_id:   ID del corso visualizzato (aggiorna il contesto se fornito).
        corso_contestuale_nome: Nome leggibile del corso (opzionale).

    Returns:
        Risposta testuale dell'agente, pronta per essere mostrata in UI.

    Esempio d'uso in una pagina Streamlit::

        from src.agents.orchestrator import chat_con_orchestratore, aggiorna_contesto_sessione

        # Una volta sola quando si carica la pagina del corso:
        aggiorna_contesto_sessione(corso_id=corso["id"], corso_nome=corso["nome"])

        # Ad ogni messaggio dell'utente:
        risposta = chat_con_orchestratore(st.session_state.input_utente)
        st.chat_message("assistant").write(risposta)
    """
    if corso_contestuale_id is not None:
        aggiorna_contesto_sessione(
            corso_id=corso_contestuale_id,
            corso_nome=corso_contestuale_nome,
        )

    # Aggiorna la variabile globale dal thread principale PRIMA di invocare
    # l'agente. I tool girano in thread background dove session_state
    # non è accessibile — leggono _STUDENTE_ID_CORRENTE dal modulo.
    _aggiorna_studente_corrente()

    # Inietta il contesto di navigazione corrente nel messaggio.
    # Il thread LangGraph mantiene la memoria delle conversazioni precedenti,
    # e l'agente potrebbe non richiamare tool_leggi_contesto se crede di
    # conoscere già il contesto. Prefissando il contesto attuale evitiamo
    # che la memoria stantia (es. "chat documento" chiusa) prevalga.
    contesto = _CONTESTO_CORRENTE
    if contesto:
        _ctx_parts: list[str] = []
        doc_chat = contesto.get("documento_chat")
        if doc_chat:
            _ctx_parts.append(f"Chat documento '{doc_chat.get('titolo', '')}'")
        else:
            if contesto.get("corso_nome"):
                _ctx_parts.append(f"Corso '{contesto['corso_nome']}'")
            if contesto.get("piano_titolo"):
                _ctx_parts.append(f"Piano '{contesto['piano_titolo']}'")
        if _ctx_parts:
            messaggio_utente = f"[CONTESTO NAVIGAZIONE: {', '.join(_ctx_parts)}]\n{messaggio_utente}"

    try:
        return esegui_agente(
            _get_orchestratore(),
            messaggio_utente,
            thread_id=_get_thread_id(),
        )
    except Exception as e:
        # Se il checkpoint contiene AIMessage con tool_calls orfani (senza
        # il corrispondente ToolMessage), la conversazione è corrotta.
        # Questo succede quando un rerun di Streamlit interrompe l'agente
        # a metà di una tool call.  Ricreiamo l'agente con un InMemorySaver
        # pulito e riproviamo — l'utente perde la cronologia LangGraph ma
        # la chat UI (chat_history_display) resta intatta.
        if "tool_calls" in str(e) and "ToolMessage" in str(e):
            st.session_state.pop(_SK_ORCHESTRATORE, None)
            st.session_state.pop(_SK_ORCHESTRATORE_DOCENTE, None)
            st.session_state.pop(_SK_THREAD_ID, None)
            return esegui_agente(
                _get_orchestratore(),
                messaggio_utente,
                thread_id=_get_thread_id(),
            )
        raise


def reset_sessione_chat() -> None:
    """Azzera agente, thread, contesto e cronologia chat. Chiamare al logout dell'utente."""
    chiavi_da_rimuovere = [
        _SK_ORCHESTRATORE,
        _SK_ORCHESTRATORE_DOCENTE,
        _SK_AGENTE_TEORICO,
        _SK_THREAD_ID,
        _SK_CONTESTO,
        "chat_history_doc",       # chat docente
        "chat_history_display",   # chat studente
    ]
    for chiave in chiavi_da_rimuovere:
        st.session_state.pop(chiave, None)
    global _CONTESTO_CORRENTE
    _CONTESTO_CORRENTE = {}
