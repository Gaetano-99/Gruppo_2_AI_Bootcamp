"""
src/agents/orientamento.py
Agente basato su LangGraph per rispondere alle domande degli ospiti sui corsi di laurea.
Supporta sia chat libera che analisi di un questionario strutturato.
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

from src.agents.dati_corsi import CATALOGO_CORSI

# ---------------------------------------------------------------------------
# Questionario strutturato
# ---------------------------------------------------------------------------
DOMANDE_QUESTIONARIO = [
    {
        "id": "pensiero",
        "testo": "Come ti descriveresti?",
        "opzioni": [
            "Logico-analitico: ragiono con dati, numeri e metodo",
            "Creativo-artistico: immagino, progetto, esprimo idee",
            "Pratico-manuale: costruisco, sperimento, risolvo con le mani",
            "Empatico-relazionale: ascolto, comunico, lavoro con le persone",
        ],
    },
    {
        "id": "area",
        "testo": "Quale ambito ti appassiona di più?",
        "opzioni": [
            "Tecnologia, informatica e ingegneria",
            "Scienze naturali, biologia o medicina",
            "Economia, finanza e management",
            "Arte, letteratura e scienze umanistiche",
            "Diritto e scienze politico-sociali",
            "Matematica e fisica teorica",
        ],
    },
    {
        "id": "carriera",
        "testo": "Che tipo di carriera immagini per te?",
        "opzioni": [
            "Ricercatore o accademico",
            "Professionista in una grande azienda",
            "Libero professionista o consulente",
            "Pubblico impiego o istituzioni",
            "Imprenditore o startupper",
        ],
    },
    {
        "id": "studio",
        "testo": "Come preferisci affrontare i problemi?",
        "opzioni": [
            "Con metodo, analisi e dati",
            "Con creatività e intuizione",
            "Con collaborazione e lavoro di squadra",
            "Con pratica diretta ed esperimenti",
        ],
    },
    {
        "id": "durata",
        "testo": "Quanto tempo sei disposto/a a dedicare agli studi universitari?",
        "opzioni": [
            "3 anni (Laurea triennale)",
            "3 + 2 anni (Triennale + Magistrale)",
            "Ciclo unico 5–6 anni (es. Medicina, Giurisprudenza, Architettura)",
        ],
    },
]

class StatoOrientamento(TypedDict):
    """Stato dell'agente di orientamento che passa attraverso i nodi."""
    domanda: str
    cronologia_chat: list[dict]
    risposta: str
    
def genera_risposta_orientamento(stato: StatoOrientamento) -> dict:
    """Invoca l'LLM fornendo come contesto il catalogo dei corsi e la system instruction."""
    domanda = stato["domanda"]
    
    # Costruiamo il contesto testuale usando la knowledge base definita in dati_corsi.py
    contesto_testo = "Catalogo dei Corsi di Laurea Disponibili all'Università:\n\n"
    for id_corso, dati in CATALOGO_CORSI.items():
        contesto_testo += f"--- {dati['nome_completo']} ---\n"
        contesto_testo += f"Descrizione: {dati['descrizione']}\n"
        contesto_testo += f"Durata: {dati['durata']}\n"
        contesto_testo += f"Materie Studiate: {', '.join(dati['materie_principali'])}\n"
        contesto_testo += f"Prospettive e Sbocchi: {', '.join(dati['sbocchi_lavorativi'])}\n\n"
        
    istruzioni_sistema = (
        "Sei un assistente per l'orientamento universitario accogliente e professionale. "
        "Il tuo compito è rispondere alle domande dei futuri studenti (ospiti) sui corsi di "
        "laurea. Utilizza ESCLUSIVAMENTE le informazioni fornite nel Contesto qui sotto.\n"
        "Se l'utente fa una domanda che non riguarda i corsi di laurea in catalogo, l'università "
        "o il percorso di studi, NON rispondere alla domanda ma redirigilo gentilmente dicendo:\n"
        "\"Posso aiutarti a scoprire informazioni sui corsi di laurea disponibili. Prova a "
        "chiedermi ad esempio cosa si studia a Ingegneria, che differenza c'è tra Matematica "
        "e Fisica, o quali sbocchi lavorativi ha Scienze della Terra.\"\n"
        "Sii chiaro, conciso e usa una formattazione leggibile (es. elenchi puntati se elenchi materie o sbocchi)."
    )
    
    # Includiamo parte della cronologia passata per dare un po' di memoria conversazionale
    storia_recente = ""
    if "cronologia_chat" in stato and stato["cronologia_chat"]:
        storia_recente = "Cronologia recente della conversazione:\n"
        # Analizziamo solo gli ultimi 4 messaggi
        for msg in stato["cronologia_chat"][-4:]:
            storia_recente += f"{msg['ruolo'].capitalize()}: {msg['contenuto']}\n"
        storia_recente += "\n"
        
    contesto_completo = contesto_testo + storia_recente
    
    # Invocazione del modello
    risposta_llm = chiedi_con_contesto(
        domanda=domanda,
        contesto=contesto_completo,
        istruzioni=istruzioni_sistema
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
        "risposta": ""
    }
    risultato = agente.invoke(stato_iniziale)
    return risultato["risposta"]


def analizza_questionario(risposte: dict[str, str]) -> str:
    """
    Analizza le risposte al questionario strutturato e restituisce
    una raccomandazione personalizzata di corsi di laurea.

    risposte: {id_domanda: testo_opzione_scelta}
    """
    # Costruisce il profilo dell'utente dalle risposte
    profilo_righe = []
    for dom in DOMANDE_QUESTIONARIO:
        risposta = risposte.get(dom["id"], "Non specificato")
        profilo_righe.append(f"- {dom['testo']}: **{risposta}**")
    profilo_testo = "\n".join(profilo_righe)

    # Catalogo dei corsi come contesto
    contesto_corsi = "Catalogo dei Corsi di Laurea Disponibili:\n\n"
    for id_corso, dati in CATALOGO_CORSI.items():
        contesto_corsi += f"--- {dati['nome_completo']} ---\n"
        contesto_corsi += f"Descrizione: {dati['descrizione']}\n"
        contesto_corsi += f"Durata: {dati['durata']}\n"
        contesto_corsi += f"Materie: {', '.join(dati['materie_principali'])}\n"
        contesto_corsi += f"Sbocchi: {', '.join(dati['sbocchi_lavorativi'])}\n\n"

    contesto_completo = f"Profilo dello studente:\n{profilo_testo}\n\n{contesto_corsi}"

    istruzioni = (
        "Sei un orientatore universitario esperto e accogliente. "
        "Hai ricevuto il profilo di un potenziale studente tramite un questionario. "
        "Basandoti ESCLUSIVAMENTE sui corsi nel catalogo fornito:\n"
        "1. Consiglia 2-3 corsi di laurea più adatti al suo profilo, spiegando brevemente perché ciascuno si adatta.\n"
        "2. Evidenzia le differenze principali tra i corsi consigliati.\n"
        "3. Concludi con un invito a fare domande per approfondire qualsiasi corso.\n"
        "Usa un tono caldo, motivante e chiaro. Usa elenchi puntati per maggiore leggibilità."
    )

    return chiedi_con_contesto(
        domanda="Analizza il mio profilo e consigliami i corsi di laurea più adatti",
        contesto=contesto_completo,
        istruzioni=istruzioni,
    )
