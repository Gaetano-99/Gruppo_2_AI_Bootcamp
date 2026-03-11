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
from platform_sdk.agent import crea_agente, esegui_agente

from src.agents.content_gen import crea_agente_content_gen, esegui_generazione
from src.agents.practice_gen import esegui_generazione_pratica
from src.agents.gap_analysis import analizza_gap

# ---------------------------------------------------------------------------
# Chiavi session_state
# ---------------------------------------------------------------------------
_SK_ORCHESTRATORE = "_orch_agente_compilato"
_SK_AGENTE_TEORICO = "_orch_agente_teorico"
_SK_THREAD_ID     = "_orch_thread_id"
_SK_CONTESTO      = "_orch_contesto_sessione"

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
# System prompt — conversazione + routing in un unico prompt coerente
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """Sei Lea, l'assistente intelligente della piattaforma LearnAI. Supporti sia studenti che docenti.

IL TUO CARATTERE:
Parli in italiano con un tono caldo, chiaro e motivante. Non sei un bot che esegue
comandi: capisci il contesto, anticipi i bisogni e rendi l'esperienza piacevole.
Dopo ogni azione completata, proponi proattivamente il passo successivo logico.

PRIMO PASSO OBBLIGATORIO:
Usa SEMPRE tool_leggi_contesto come prima azione per capire:
- Chi sta parlando (studente o docente)
- Quale corso è visualizzato
Adatta il comportamento in base al ruolo rilevato.

--- MODALITÀ DOCENTE ---
Sei attivo in modalità DOCENTE quando tool_leggi_contesto restituisce "L'utente è un DOCENTE".

COSA SAI FARE PER IL DOCENTE:
1. tool_leggi_contesto        → capire il corso selezionato e il ruolo corrente.
2. tool_analizza_classe       → analizzare performance studenti, argomenti difficili, rischio abbandono.
3. tool_esplora_catalogo      → esplorare i materiali caricati nel corso.
4. tool_genera_corso          → generare una lezione teorica su un argomento del corso.
5. tool_genera_pratica        → creare quiz o flashcard per gli studenti.

REGOLE DOCENTE:
- Quando il docente chiede "analizza le risposte", "andamento della classe", "studenti in difficoltà"
  o simili → usa SEMPRE tool_analizza_classe (non rispondere a memoria).
- Puoi generare lezioni e quiz che vengono salvati come contenuto ufficiale del corso.
- Non dire al docente di usare "il piano personalizzato": i docenti gestiscono corsi, non piani.
- Dopo ogni analisi, suggerisci azioni concrete: es. rivedere l'argomento, creare esercizi mirati.

--- MODALITÀ STUDENTE ---
Sei attivo in modalità STUDENTE quando tool_leggi_contesto non indica ruolo docente.

COSA SAI FARE PER LO STUDENTE:
1. tool_leggi_contesto          → sapere quale corso sta visualizzando lo studente e il piano attivo.
2. tool_esplora_catalogo        → scoprire corsi o materiali disponibili (con ID materiale).
3. tool_genera_corso            → creare una nuova lezione teorica su un argomento.
                                  Accetta un parametro opzionale materiale_id per generare
                                  la lezione SOLO dal contenuto di quel materiale specifico.
4. tool_genera_pratica          → creare quiz, flashcard o schemi su una sezione studiata.
5. tool_analizza_preparazione   → analizzare i risultati di un quiz e identificare lacune.
6. tool_modifica_piano          → rinominare, riordinare, eliminare, aggiungere capitoli/paragrafi,
                                  LEGGERE e RISCRIVERE il testo di una lezione.

REGOLE STUDENTE:
- I CORSI UNIVERSITARI sono in sola lettura. Non puoi modificarli.
- I PIANI PERSONALIZZATI sono spazi privati dello studente. Quando generi contenuti,
  stai sempre creando un PIANO PERSONALIZZATO — mai modificando il corso ufficiale.
- MATERIALE SELEZIONATO: se tool_leggi_contesto riporta "Materiale selezionato", lo studente
  vuole una lezione su quel materiale specifico. Usa SUBITO tool_genera_corso passando
  il materiale_id indicato nel contesto. Se non c'è un corso associato, usa corso_universitario_id=0.
  Non chiedere conferme.
- MATERIALE SENZA CORSO: se lo studente vuole una lezione da materiali personali non legati
  a nessun corso, usa tool_genera_corso con corso_universitario_id=0 e il materiale_id appropriato.
- Quando lo studente chiede di riscrivere, modificare, semplificare, espandere un paragrafo:
  1. Chiama tool_leggi_contesto → ottieni piano_id e l'elenco "Sezioni del piano" con gli ID.
  2. Identifica il paragrafo_id dal nome (corrispondenza parziale se necessario).
  3. Chiama tool_modifica_piano(piano_id, 'leggi_contenuto', paragrafo_id) per leggere il testo attuale.
  4. Genera il testo riscritto in modo completo e dettagliato.
  5. Chiama tool_modifica_piano(piano_id, 'riscrivi_contenuto', paragrafo_id, nuovo_testo).
  NON chiedere mai il numero del piano all'utente: è già nel contesto.
  NON dire mai che non puoi modificare il testo: hai sempre questo percorso disponibile.

--- REGOLE COMUNI ---
- Se l'utente fa small talk o saluta, rispondi naturalmente senza invocare tool.
- Se la richiesta è ambigua, fai UNA sola domanda mirata.
- Non mostrare mai ID numerici interni all'utente.
- Gestisci gli errori con empatia e suggerisci il passo successivo.
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
        return "Nessun contesto attivo. L'utente non ha ancora selezionato un corso."

    parti = []
    tipo = contesto.get("tipo_vista")
    if tipo == "docente":
        parti.append("L'utente è un DOCENTE. Usa la modalità docente: analisi classe, gestione corso.")
    elif tipo == "corso":
        parti.append("L'utente sta visualizzando un CORSO universitario (sola lettura).")
    elif tipo == "piano":
        parti.append("L'utente sta studiando nel proprio PIANO PERSONALIZZATO.")

    if contesto.get("corso_id"):
        nome = contesto.get("corso_nome", "nome non disponibile")
        parti.append(f"Corso: ID {contesto['corso_id']} — {nome}")

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

    # Materiale selezionato dallo studente tramite il pannello "Visualizza materiale"
    mat = contesto.get("materiale_selezionato")
    if mat:
        corso_id_mat = mat.get("corso_id") or 0  # 0 = nessun corso associato
        parti.append(
            f"Materiale selezionato dallo studente: '{mat['titolo']}' "
            f"(materiale_id={mat['id']}, corso_id={corso_id_mat}). "
            f"Genera una lezione su questo materiale chiamando tool_genera_corso "
            f"con corso_universitario_id={corso_id_mat} e materiale_id={mat['id']}."
        )

    return "\n".join(parti) if parti else "Contesto parziale: nessuna sezione generata ancora."


@tool
def tool_esplora_catalogo(tipo_ricerca: str, corso_universitario_id: int = None) -> str:
    """
    Scopri i corsi universitari disponibili o i materiali di un corso specifico.
    - tipo_ricerca='corsi'     → lista tutti i corsi attivi.
    - tipo_ricerca='argomenti' → materiali del corso (richiede corso_universitario_id).
    """
    if tipo_ricerca == "corsi":
        corsi = db.trova_tutti("corsi_universitari", {"attivo": 1})
        if not corsi:
            return "Nessun corso universitario attivo nel sistema."
        return "Corsi disponibili:\n" + "\n".join(
            f"- ID {c['id']}: {c['nome']}" for c in corsi
        )

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

    return "Errore: tipo_ricerca deve essere 'corsi' o 'argomenti'."


@tool
def tool_genera_corso(corso_universitario_id: int, argomento: str, materiale_id: int = 0) -> str:
    """
    Genera e salva un corso teorico completo su un argomento specifico.
    Usa quando l'utente chiede di creare una lezione, un corso o approfondire un tema.

    Parametro corso_universitario_id: usa 0 se non c'è un corso associato (es. materiale personale).
    Parametro opzionale materiale_id: se > 0, la lezione viene generata usando SOLO
    i contenuti di quel materiale specifico (utile quando lo studente ha selezionato
    un documento dal pannello "Visualizza materiale").
    """
    # Usa la variabile globale aggiornata dal thread principale prima dell'invocazione
    studente_id = _STUDENTE_ID_CORRENTE

    # corso_id=0 è il sentinella per "nessun corso": passa None al motore
    corso_id_eff = corso_universitario_id if corso_universitario_id and corso_universitario_id > 0 else None

    stato_finale = esegui_generazione(
        agente=_get_agente_teorico(),
        corso_id=corso_id_eff,
        argomento_richiesto=argomento,
        docente_id=studente_id,
        is_corso_docente=False,
        materiale_id=materiale_id if materiale_id and materiale_id > 0 else None,
    )

    if stato_finale.get("errore"):
        return f"Errore durante la generazione: {stato_finale['errore']}"

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
def tool_genera_pratica(paragrafo_id: int, strumenti: list[str]) -> str:
    """
    Genera strumenti pratici (quiz, flashcard, schema) per una sezione studiata.
    strumenti: lista con uno o più tra "quiz", "flashcard", "schema".
    """
    studente_id = _STUDENTE_ID_CORRENTE

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
def tool_modifica_piano(piano_id: int, azione: str, target_id: int, nuovo_valore: str = "") -> str:
    """
    Modifica la struttura o il contenuto di un piano personalizzato dello studente.

    azione può essere:
      - 'rinomina_capitolo'       → rinomina piano_capitoli.titolo (target_id = capitolo_id)
      - 'rinomina_paragrafo'      → rinomina piano_paragrafi.titolo (target_id = paragrafo_id)
      - 'riordina_capitolo'       → sposta il capitolo in una nuova posizione (nuovo_valore = intero)
      - 'riordina_paragrafo'      → sposta il paragrafo in una nuova posizione (nuovo_valore = intero)
      - 'elimina_capitolo'        → elimina il capitolo e tutti i suoi paragrafi (target_id = capitolo_id)
      - 'elimina_paragrafo'       → elimina il paragrafo e i suoi contenuti (target_id = paragrafo_id)
      - 'aggiungi_capitolo'       → aggiunge un nuovo capitolo al piano (nuovo_valore = titolo)
      - 'sposta_paragrafo'        → sposta il paragrafo in un altro capitolo (target_id = paragrafo_id,
                                    nuovo_valore = capitolo_id di destinazione come stringa intera).
                                    Usalo per riorganizzare paragrafi tra capitoli diversi.
      - 'leggi_contenuto'         → legge il testo attuale di un paragrafo (target_id = paragrafo_id).
                                    Usalo PRIMA di riscrivere, per basare la riscrittura sul testo originale.
      - 'riscrivi_contenuto'      → sostituisce il testo di un paragrafo (target_id = paragrafo_id,
                                    nuovo_valore = testo completo riscritto). Il testo deve essere
                                    completo e ben strutturato, non un riassunto.

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
                db.aggiorna(
                    "piano_contenuti",
                    {"paragrafo_id": target_id, "tipo": "lezione"},
                    {"contenuto_json": nuovo_valore.strip()},
                )
            else:
                db.inserisci("piano_contenuti", {
                    "paragrafo_id": target_id,
                    "tipo": "lezione",
                    "contenuto_json": nuovo_valore.strip(),
                })
            return f"✅ Paragrafo '{titolo}' riscritto e salvato nel piano. Lo studente vedrà la nuova versione al prossimo caricamento."

        else:
            return f"Azione '{azione}' non riconosciuta. Azioni valide: rinomina_capitolo, rinomina_paragrafo, riordina_capitolo, riordina_paragrafo, elimina_capitolo, elimina_paragrafo, aggiungi_capitolo, sposta_paragrafo, leggi_contenuto, riscrivi_contenuto."

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
    """Orchestratore: singleton in session_state con memoria LangGraph intatta."""

    #if _USER_ROLE = "docente":
    #     system_pompt = DOCENTE_SYSTEM_PROMPT
    # else:
    #     system_pompt = _SYSTEM_PROMPT

    if _SK_ORCHESTRATORE not in st.session_state:
        st.session_state[_SK_ORCHESTRATORE] = crea_agente(
            tools=[
                tool_leggi_contesto,
                tool_esplora_catalogo,
                tool_genera_corso,
                tool_genera_pratica,
                tool_analizza_preparazione,
                tool_modifica_piano,
                tool_analizza_classe,
            ],
            system_prompt=_SYSTEM_PROMPT,
            memoria=True,
        )
    return st.session_state[_SK_ORCHESTRATORE]


def _get_thread_id() -> str:
    """Thread ID stabile per sessione utente, usato dal checkpointer di LangGraph."""
    if _SK_THREAD_ID not in st.session_state:
        user_id = st.session_state.get("user", {}).get("user_id", "anonimo")
        st.session_state[_SK_THREAD_ID] = f"lea_sessione_{user_id}"
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
    clear_materiale: bool = False,
    clear_corso: bool = False,
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
    if clear_materiale:
        contesto.pop("materiale_selezionato", None)
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

    return esegui_agente(
        _get_orchestratore(),
        messaggio_utente,
        thread_id=_get_thread_id(),
    )


def reset_sessione_chat() -> None:
    """Azzera agente, thread, contesto e cronologia chat. Chiamare al logout dell'utente."""
    chiavi_da_rimuovere = [
        _SK_ORCHESTRATORE,
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
