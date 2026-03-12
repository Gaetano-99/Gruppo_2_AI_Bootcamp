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

from platform_sdk.database import db
from src.agents.dati_questionario import QUESTIONARIO_ORIENTAMENTO

class StatoOrientamento(TypedDict):
    """Stato dell'agente di orientamento che passa attraverso i nodi."""
    domanda: str
    cronologia_chat: list[dict]
    risposta: str
    
def genera_risposta_orientamento(stato: StatoOrientamento) -> dict:
    """Invoca l'LLM fornendo come contesto il catalogo dei corsi e la system instruction."""
    domanda = stato["domanda"]
    
    # Costruiamo il contesto testuale usando il database
    corsi = db.trova_tutti("corsi_di_laurea", ordine="facolta ASC, nome ASC")
    contesto_testo = "Catalogo dei Corsi di Laurea Disponibili all'Università:\n\n"
    for corso in corsi:
        contesto_testo += f"--- {corso['nome']} ---\n"
        if corso['descrizione']:
            contesto_testo += f"Descrizione: {corso['descrizione']}\n"
        if corso['durata']:
            contesto_testo += f"Durata: {corso['durata']}\n"
        
        import json
        if corso['materie_principali_json']:
            try:
                materie = json.loads(corso['materie_principali_json'])
                contesto_testo += f"Materie Studiate: {', '.join(materie)}\n"
            except:
                pass
        if corso['sbocchi_lavorativi_json']:
            try:
                sbocchi = json.loads(corso['sbocchi_lavorativi_json'])
                contesto_testo += f"Prospettive e Sbocchi: {', '.join(sbocchi)}\n"
            except:
                pass
        contesto_testo += "\n"
        
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

def analizza_risposte_questionario(risposte_dict: dict) -> str:
    """Legge le risposte del questionario e restituisce un consiglio personalizzato via LLM."""
    testo_risposte = "RISPOSTE DEL CANDIDATO AL QUESTIONARIO ATTITUDINALE:\n\n"
    for q in QUESTIONARIO_ORIENTAMENTO:
        qid = q["id"]
        if qid in risposte_dict:
            testo_risposte += f"Domanda: {q['domanda']}\nRisposta: {risposte_dict[qid]}\n\n"
            
    corsi = db.trova_tutti("corsi_di_laurea", ordine="facolta ASC, nome ASC")
    contesto_corsi = "CATALOGO CORSI DISPONIBILI:\n\n"
    for corso in corsi:
        contesto_corsi += f"- {corso['nome']} (Area: {corso['facolta']})\n"
        if corso['descrizione']: contesto_corsi += f"  Descrizione: {corso['descrizione']}\n"
        if corso['materie_principali_json']:
            import json
            try:
                materie = json.loads(corso['materie_principali_json'])
                contesto_corsi += f"  Materie: {', '.join(materie)}\n"
            except: pass
        contesto_corsi += "\n"
        
    istruzioni = (
        "Sei un esperto consulente di orientamento universitario. "
        "Analizza attentamente le risposte fornite dal candidato al questionario attitudinale. "
        "Basandoti sulle sue preferenze, inclinazioni e obiettivi, "
        "determina il percorso di studi più adatto a lui scegliendo ESCLUSIVAMENTE tra i corsi nel catalogo fornito.\n"
        "Fornisci una risposta così strutturata:\n"
        "1. **Il tuo profilo**: Una breve sintesi delle inclinazioni emerse dalle risposte.\n"
        "2. **Corsi consigliati**: Il Corso di Laurea (o un paio di varianti) maggiormente adatti, con il rispettivo link o area.\n"
        "3. **Perché fa per te**: La motivazione per cui questi corsi si adattano al profilo del candidato.\n"
        "Usa una formattazione markdown leggibile, un tono professionale, empatico e incoraggiante."
    )
    
    prompt = f"{testo_risposte}\n\n{contesto_corsi}"
    
    risultato = chiedi_con_contesto(
        domanda="Basandoti sulle mie risposte, qual è il percorso di studi più adatto per me?",
        contesto=prompt,
        istruzioni=istruzioni
    )
    return risultato

