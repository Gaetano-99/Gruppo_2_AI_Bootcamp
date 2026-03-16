"""
src/agents/orientamento.py
Agente basato su LangGraph per rispondere alle domande degli ospiti sui corsi di laurea.
Supporta sia chat libera che analisi di un questionario di orientamento esteso (30 domande).

Il catalogo dei corsi viene caricato dal database (tabella corsi_di_laurea)
anziché da un file statico, per garantire dati sempre aggiornati.
"""

from __future__ import annotations
from typing import TypedDict
from langgraph.graph import StateGraph, END

# Import con fallback per gestire diverse possibili strutture del PYTHONPATH nel progetto
try:
    from core.llm import chiedi_con_contesto
except ImportError:
    try:
        from platform_sdk.llm import chiedi_con_contesto
    except ImportError:
        from llm import chiedi_con_contesto

try:
    from platform_sdk.database import db
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
        from platform_sdk.database import db
    except ImportError:
        db = None

# ---------------------------------------------------------------------------
# Caricamento catalogo corsi dal Database
# ---------------------------------------------------------------------------

def carica_catalogo_da_db() -> list[dict]:
    """
    Carica il catalogo dei corsi di laurea dalla tabella corsi_di_laurea nel DB.
    Ritorna una lista di dizionari con chiavi: id, nome, facolta, descrizione.
    Fallback su lista vuota se il DB non è disponibile.
    """
    if db is None:
        return []
    try:
        corsi = db.trova_tutti("corsi_di_laurea", ordine="facolta ASC, nome ASC")
        return corsi or []
    except Exception:
        return []


def _build_contesto_corsi(corsi: list[dict]) -> str:
    """Costruisce il testo del catalogo corsi da passare al LLM come contesto."""
    if not corsi:
        return "Nessun corso di laurea disponibile al momento."
    righe = ["Catalogo dei Corsi di Laurea Disponibili:\n"]
    for c in corsi:
        righe.append(f"--- {c.get('nome', 'N/D')} ({c.get('facolta', 'N/D')}) ---")
        desc = c.get("descrizione") or "Nessuna descrizione disponibile."
        righe.append(f"Descrizione: {desc}\n")
    return "\n".join(righe)


# ---------------------------------------------------------------------------
# Questionario di orientamento esteso — 30 domande, 4 opzioni ciascuna
# ---------------------------------------------------------------------------

DOMANDE_QUESTIONARIO = [
    # SEZIONE 1 — Personalità e stile cognitivo (domande 1–8)
    {
        "id": "q01",
        "categoria": "Personalità",
        "testo": "Come ti descriveresti?",
        "opzioni": [
            "Logico-analitico: ragiono con dati, numeri e metodo",
            "Creativo-artistico: immagino, progetto, esprimo idee",
            "Pratico-operativo: costruisco, sperimento, risolvo con le mani",
            "Empatico-relazionale: ascolto, comunico, lavoro con le persone",
        ],
    },
    {
        "id": "q02",
        "categoria": "Personalità",
        "testo": "Quando hai un problema difficile, come preferisci affrontarlo?",
        "opzioni": [
            "Analizzo i dati e cerco la soluzione più efficiente",
            "Cerco soluzioni creative e non convenzionali",
            "Chiedo consiglio ad altri e lavoro in team",
            "Mi affido all'intuito e all'esperienza pratica",
        ],
    },
    {
        "id": "q03",
        "categoria": "Personalità",
        "testo": "Quale di queste attività ti dà più soddisfazione?",
        "opzioni": [
            "Risolvere un problema matematico complesso",
            "Creare qualcosa di bello o originale",
            "Aiutare qualcuno in difficoltà",
            "Costruire o riparare qualcosa con le proprie mani",
        ],
    },
    {
        "id": "q04",
        "categoria": "Personalità",
        "testo": "Come gestisci il tuo tempo di studio?",
        "opzioni": [
            "Con metodo rigoroso: schema, scaletta, ripasso",
            "In modo creativo: mappe visive, colori, associazioni",
            "In gruppo: mi confronto con i compagni",
            "Praticando direttamente: esercizi, laboratori, esempi reali",
        ],
    },
    {
        "id": "q05",
        "categoria": "Personalità",
        "testo": "Quale ruolo assumi naturalmente in un gruppo di lavoro?",
        "opzioni": [
            "Il pianificatore: organizzo, stabilisco le priorità",
            "Il creativo: propongo idee nuove",
            "Il mediatore: facilito il dialogo e la coesione",
            "L'esecutore: realizzo concretamente le cose",
        ],
    },
    {
        "id": "q06",
        "categoria": "Personalità",
        "testo": "Cosa ti motiva di più nel lavoro?",
        "opzioni": [
            "Risolvere problemi complessi e trovare soluzioni innovative",
            "Esprimere la mia creatività e lasciare un segno",
            "Fare la differenza nella vita delle persone",
            "Vedere risultati concreti e tangibili del mio lavoro",
        ],
    },
    {
        "id": "q07",
        "categoria": "Personalità",
        "testo": "Come ti comporti davanti all'incertezza?",
        "opzioni": [
            "Cerco dati e informazioni per ridurre l'incertezza",
            "Improvviso e mi adatto con flessibilità",
            "Consulto più persone per avere prospettive diverse",
            "Procedo passo dopo passo con prove ed errori",
        ],
    },
    {
        "id": "q08",
        "categoria": "Personalità",
        "testo": "Quale frase ti rappresenta meglio?",
        "opzioni": [
            "\"I numeri non mentono mai\"",
            "\"La bellezza è nella differenza\"",
            "\"Insieme si va più lontano\"",
            "\"Imparo facendo\"",
        ],
    },
    # SEZIONE 2 — Interessi e materie preferite (domande 9–16)
    {
        "id": "q09",
        "categoria": "Interessi",
        "testo": "Quale area ti appassiona di più?",
        "opzioni": [
            "Tecnologia, informatica e ingegneria",
            "Scienze naturali, biologia o medicina",
            "Economia, finanza e management",
            "Arte, letteratura, storia e scienze umanistiche",
        ],
    },
    {
        "id": "q10",
        "categoria": "Interessi",
        "testo": "Quale materia scolastica hai trovato più stimolante?",
        "opzioni": [
            "Matematica e Informatica",
            "Biologia, Chimica o Fisica",
            "Storia, Filosofia o Letteratura",
            "Arte, Disegno o Musica",
        ],
    },
    {
        "id": "q11",
        "categoria": "Interessi",
        "testo": "Quale di questi temi ti affascina di più?",
        "opzioni": [
            "Intelligenza artificiale e robotica",
            "Ambiente, sostenibilità e cambiamento climatico",
            "Economia globale e mercati finanziari",
            "Psicologia umana e dinamiche sociali",
        ],
    },
    {
        "id": "q12",
        "categoria": "Interessi",
        "testo": "Quale tipo di lettura preferisci nel tempo libero?",
        "opzioni": [
            "Saggi scientifici o tecnologici",
            "Romanzi, poesia o filosofia",
            "Economia, business e biografie di imprenditori",
            "Medicina, salute e benessere",
        ],
    },
    {
        "id": "q13",
        "categoria": "Interessi",
        "testo": "Quale dei questi eventi ti piacerebbe frequentare?",
        "opzioni": [
            "Hackathon o conferenza tecnologica",
            "Mostra d'arte o festival letterario",
            "Forum economico o startup pitch",
            "Convegno medico-scientifico",
        ],
    },
    {
        "id": "q14",
        "categoria": "Interessi",
        "testo": "Quale aspetto della società ti interessa maggiormente migliorare?",
        "opzioni": [
            "L'innovazione tecnologica e digitale",
            "La giustizia sociale e i diritti umani",
            "La salute pubblica e il benessere",
            "L'economia e l'occupazione",
        ],
    },
    {
        "id": "q15",
        "categoria": "Interessi",
        "testo": "Cosa fai più spesso nel tempo libero?",
        "opzioni": [
            "Programmo, gioco con la tecnologia, costruisco gadget",
            "Creo arte, musica, scrivo o fotografo",
            "Leggo, studio argomenti storici o filosofici",
            "Faccio sport, volontariato o sto con le persone",
        ],
    },
    {
        "id": "q16",
        "categoria": "Interessi",
        "testo": "Quale progetto ti affascinerebbe di più realizzare?",
        "opzioni": [
            "Un'app o algoritmo che risolve un problema reale",
            "Un libro, un'opera d'arte o un'installazione culturale",
            "Una startup o un piano di business innovativo",
            "Un programma di assistenza per persone vulnerabili",
        ],
    },
    # SEZIONE 3 — Carriera e obiettivi professionali (domande 17–22)
    {
        "id": "q17",
        "categoria": "Carriera",
        "testo": "Che tipo di carriera immagini per te?",
        "opzioni": [
            "Ricercatore o accademico in un campo scientifico",
            "Professionista tecnico in una grande azienda",
            "Libero professionista o consulente autonomo",
            "Imprenditore o fondatore di startup",
        ],
    },
    {
        "id": "q18",
        "categoria": "Carriera",
        "testo": "Quale ambiente lavorativo preferiresti?",
        "opzioni": [
            "Laboratorio o torre di ricerca con sfide intellettuali",
            "Studio creativo o agenzia dinamica",
            "Ospedale, clinica o ente pubblico per il bene comune",
            "Ufficio aziendale internazionale o sede di startup",
        ],
    },
    {
        "id": "q19",
        "categoria": "Carriera",
        "testo": "Quanto è importante per te la stabilità economica nella scelta della carriera?",
        "opzioni": [
            "Molto: preferisco sicurezza e stipendio garantito",
            "Abbastanza: mi serve una base solida ma voglio crescere",
            "Poco: preferisco passione e significato al denaro",
            "Per niente: sono disposto a rischiare per fare grandi cose",
        ],
    },
    {
        "id": "q20",
        "categoria": "Carriera",
        "testo": "Dove vorresti lavorare geograficamente?",
        "opzioni": [
            "In Italia, vicino alla mia città",
            "In un'altra città italiana (es. Milano, Roma)",
            "All'estero, in Europa o nel mondo",
            "Non ho preferenze: lavoro anche da remoto ovunque",
        ],
    },
    {
        "id": "q21",
        "categoria": "Carriera",
        "testo": "Quale aspetto di un lavoro valorizza di più?",
        "opzioni": [
            "L'impatto sulla società e sul mondo",
            "La creatività e la libertà espressiva",
            "Lo stipendio e la progressione di carriera",
            "La varietà dei compiti e la sfida continua",
        ],
    },
    {
        "id": "q22",
        "categoria": "Carriera",
        "testo": "In quale settore vorresti lavorare?",
        "opzioni": [
            "Tech, AI, Cybersecurity o Ingegneria",
            "Sanità, Medicina o Ricerca Biomedica",
            "Finanza, Consulenza o Management",
            "Cultura, Media, Arte o Istruzione",
        ],
    },
    # SEZIONE 4 — Studio e percorso accademico (domande 23–28)
    {
        "id": "q23",
        "categoria": "Studio",
        "testo": "Quanto tempo sei disposto/a a dedicare agli studi universitari?",
        "opzioni": [
            "3 anni (Laurea triennale, poi entro nel mondo del lavoro)",
            "3+2 anni (Triennale + Magistrale)",
            "Ciclo unico 5–6 anni (es. Medicina, Giurisprudenza)",
            "Non ho ancora deciso: voglio capire meglio",
        ],
    },
    {
        "id": "q24",
        "categoria": "Studio",
        "testo": "Qual è il tuo approccio allo studio universitario ideale?",
        "opzioni": [
            "Lezioni teoriche, libri, approfondimento autonomo",
            "Laboratori, esperimenti e tirocini pratici",
            "Progetti di gruppo e discussioni collaborative",
            "Mix equilibrato di teoria e pratica",
        ],
    },
    {
        "id": "q25",
        "categoria": "Studio",
        "testo": "Cosa hai trovato più utile nella scuola superiore?",
        "opzioni": [
            "Le materie scientifiche e l'approccio metodico",
            "Le materie umanistiche e l'espressione critica",
            "I gruppi di lavoro e i progetti interdisciplinari",
            "I laboratori e le attività pratiche",
        ],
    },
    {
        "id": "q26",
        "categoria": "Studio",
        "testo": "Quanto ti interessano le lingue straniere e il contesto internazionale?",
        "opzioni": [
            "Molto: voglio studiare o lavorare all'estero",
            "Abbastanza: le lingue mi piacciono ma non è la priorità",
            "Poco: preferisco lavorare in Italia",
            "Per niente: non è un mio obiettivo",
        ],
    },
    {
        "id": "q27",
        "categoria": "Studio",
        "testo": "Come valuti le tue competenze in matematica?",
        "opzioni": [
            "Ottime: la matematica è il mio punto di forza",
            "Buone: mi trovo a mio agio con i numeri",
            "Sufficienti: non è il mio forte ma me la cavo",
            "Scarse: preferisco evitare ambiti molto matematici",
        ],
    },
    {
        "id": "q28",
        "categoria": "Studio",
        "testo": "Hai già un'idea del percorso universitario che ti interessa?",
        "opzioni": [
            "Sì, ho le idee chiare su cosa voglio studiare",
            "Ho alcune preferenze ma non ho ancora deciso",
            "Sono molto indeciso/a tra più ambiti",
            "Non ho ancora idea e voglio essere orientato/a",
        ],
    },
    # SEZIONE 5 — Valori e visione del mondo (domande 29–30)
    {
        "id": "q29",
        "categoria": "Valori",
        "testo": "Quale valore guida principalmente le tue scelte?",
        "opzioni": [
            "Razionalità e ricerca della verità oggettiva",
            "Libertà creativa e autenticità",
            "Solidarietà e cura del prossimo",
            "Ambizione e desiderio di successo",
        ],
    },
    {
        "id": "q30",
        "categoria": "Valori",
        "testo": "Come vorresti essere ricordato/a tra 20 anni?",
        "opzioni": [
            "Come uno scienziato/ingegnere che ha cambiato il modo in cui funziona il mondo",
            "Come un artista o pensatore che ha arricchito la cultura",
            "Come qualcuno che ha aiutato concretamente molte persone",
            "Come un imprenditore o leader che ha creato opportunità",
        ],
    },
]


# ---------------------------------------------------------------------------
# Grafo LangGraph per la chat libera degli ospiti
# ---------------------------------------------------------------------------

class StatoOrientamento(TypedDict):
    """Stato dell'agente di orientamento che passa attraverso i nodi."""
    domanda: str
    cronologia_chat: list[dict]
    risposta: str


def genera_risposta_orientamento(stato: StatoOrientamento) -> dict:
    """Invoca l'LLM fornendo come contesto il catalogo corsi dal DB e le istruzioni di sistema."""
    domanda = stato["domanda"]

    # Carica il catalogo dei corsi dal DB
    corsi = carica_catalogo_da_db()
    contesto_testo = _build_contesto_corsi(corsi)

    istruzioni_sistema = (
        "Sei Lea, un assistente per l'orientamento universitario accogliente e professionale. "
        "Il tuo compito è rispondere alle domande dei futuri studenti (ospiti) sui corsi di "
        "laurea. Utilizza ESCLUSIVAMENTE le informazioni fornite nel Contesto qui sotto.\n"
        "Se l'utente fa una domanda che non riguarda i corsi di laurea in catalogo, l'università "
        "o il percorso di studi, NON rispondere alla domanda ma redirigilo gentilmente dicendo:\n"
        "\"Posso aiutarti a scoprire informazioni sui corsi di laurea disponibili. Prova a "
        "chiedermi ad esempio cosa si studia a Ingegneria, che differenza c'è tra Matematica "
        "e Fisica, o quali sbocchi lavorativi ha Scienze della Terra.\"\n"
        "Sii chiaro, conciso e usa una formattazione leggibile (es. elenchi puntati se elenchi materie o sbocchi)."
    )

    # Cronologia recente per memoria conversazionale
    storia_recente = ""
    if stato.get("cronologia_chat"):
        storia_recente = "Cronologia recente della conversazione:\n"
        for msg in stato["cronologia_chat"][-4:]:
            storia_recente += f"{msg['ruolo'].capitalize()}: {msg['contenuto']}\n"
        storia_recente += "\n"

    contesto_completo = contesto_testo + "\n" + storia_recente

    risposta_llm = chiedi_con_contesto(
        domanda=domanda,
        contesto=contesto_completo,
        istruzioni=istruzioni_sistema,
    )

    return {"risposta": risposta_llm}


def crea_agente_orientamento():
    """Compila il grafo LangGraph per l'orientamento ospite."""
    grafo = StateGraph(StatoOrientamento)
    grafo.add_node("rispondi", genera_risposta_orientamento)
    grafo.set_entry_point("rispondi")
    grafo.add_edge("rispondi", END)
    return grafo.compile()


def chiedi_agente_ospite(domanda: str, cronologia: list[dict] | None = None) -> str:
    """Helper sincrono semplice per invocare l'agente e restituire la stringa risposta."""
    agente = crea_agente_orientamento()
    stato_iniziale = {
        "domanda": domanda,
        "cronologia_chat": cronologia or [],
        "risposta": "",
    }
    risultato = agente.invoke(stato_iniziale)
    return risultato["risposta"]


# ---------------------------------------------------------------------------
# Analisi del questionario esteso — 30 domande
# ---------------------------------------------------------------------------

def analizza_questionario_esteso(risposte: dict[str, str]) -> str:
    """
    Analizza le risposte al questionario di orientamento esteso (30 domande) e
    restituisce una raccomandazione personalizzata del percorso di studi.

    risposte: {id_domanda: testo_opzione_scelta}
    """
    # Raggruppa le risposte per categoria
    profilo_righe = []
    categorie_viste = set()
    for dom in DOMANDE_QUESTIONARIO:
        risposta = risposte.get(dom["id"], "Non specificato")
        cat = dom.get("categoria", "Generale")
        if cat not in categorie_viste:
            profilo_righe.append(f"\n**{cat}:**")
            categorie_viste.add(cat)
        profilo_righe.append(f"- {dom['testo']}: **{risposta}**")
    profilo_testo = "\n".join(profilo_righe)

    # Catalogo corsi dal DB
    corsi = carica_catalogo_da_db()
    contesto_corsi = _build_contesto_corsi(corsi)

    contesto_completo = (
        f"Profilo dello studente (risultato questionario 30 domande):\n{profilo_testo}\n\n"
        f"{contesto_corsi}"
    )

    istruzioni = (
        "Sei un orientatore universitario esperto, empatico e professionale. "
        "Hai ricevuto il profilo dettagliato di un potenziale studente tramite un questionario di 30 domande. "
        "Basandoti ESCLUSIVAMENTE sui corsi nel catalogo fornito:\n"
        "1. Analizza il profilo e identifica i tratti dominanti (es. attitudine analitica, creativa, relazionale).\n"
        "2. Consiglia 2-3 corsi di laurea più adatti al suo profilo, spiegando chiaramente il perché.\n"
        "3. Per ciascun corso consigliato, evidenzia brevemente i punti di forza e gli sbocchi lavorativi.\n"
        "4. Se ci sono corsi alternativi interessanti da considerare, menzionali brevemente.\n"
        "5. Concludi con un messaggio motivante e un invito a usare la chat per approfondire.\n"
        "Usa un tono caldo, motivante e professionale. Usa titoli e elenchi puntati per la leggibilità."
    )

    return chiedi_con_contesto(
        domanda="Analizza il mio profilo completo e consigliami il percorso di studi più adatto a me",
        contesto=contesto_completo,
        istruzioni=istruzioni,
    )
