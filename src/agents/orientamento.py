"""
src/agents/orientamento.py
Agente basato su LangGraph per rispondere alle domande degli ospiti sui corsi di laurea.
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
