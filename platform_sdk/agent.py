# ============================================================================
# LearnAI Platform SDK — Modulo Agente
# Funzioni per creare agenti LangGraph con tool personalizzati.
#
# Un "agente" è un'AI che può usare strumenti (tool) per completare un compito.
# Per esempio: un agente che può cercare nel database, generare testi, etc.
#
# Uso:
#   from platform_sdk.agent import crea_agente, esegui_agente
# ============================================================================

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from platform_sdk.llm import get_llm


def crea_agente(tools: list, system_prompt: str = "", memoria: bool = True):
    """
    Crea un agente LangGraph con i tool specificati.
    L'agente può ragionare e decidere quale tool usare per rispondere.

    Parametri:
        tools:         lista di funzioni decorate con @tool
        system_prompt: istruzioni di sistema per l'agente
        memoria:       se True, l'agente ricorda le conversazioni precedenti

    Ritorna:
        Un agente LangGraph pronto all'uso

    Esempio:
        from langchain_core.tools import tool

        @tool
        def cerca_corsi(query: str) -> str:
            '''Cerca corsi nel catalogo formativo'''
            risultati = db.trova_tutti("courses")
            return str(risultati)

        @tool
        def conta_utenti() -> str:
            '''Conta il numero totale di utenti nella piattaforma'''
            n = db.conta("users")
            return f"Ci sono {n} utenti registrati."

        agente = crea_agente(
            tools=[cerca_corsi, conta_utenti],
            system_prompt="Sei un assistente della piattaforma LearnAI. Rispondi in italiano."
        )
    """
    llm = get_llm()

    # Configura la memoria (per mantenere la storia della conversazione)
    checkpointer = InMemorySaver() if memoria else None

    # Crea l'agente ReAct con LangGraph
    agente = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=checkpointer,
        prompt=system_prompt if system_prompt else None,
    )

    return agente


def esegui_agente(agente, messaggio: str, thread_id: str = "default") -> str:
    """
    Invia un messaggio a un agente e ottieni la risposta.

    Parametri:
        agente:    l'agente creato con crea_agente()
        messaggio: il messaggio dell'utente
        thread_id: identificativo della conversazione (per la memoria)

    Ritorna:
        La risposta dell'agente come stringa

    Esempio:
        risposta = esegui_agente(agente, "Quanti utenti sono registrati?")
        print(risposta)

        # Seconda domanda nella stessa conversazione
        risposta2 = esegui_agente(agente, "E quanti corsi ci sono?", thread_id="conv_1")
    """
    config = {"configurable": {"thread_id": thread_id}}

    risultato = agente.invoke(
        {"messages": [{"role": "user", "content": messaggio}]},
        config=config,
    )

    # Estrai l'ultimo messaggio dell'assistente
    messaggi = risultato.get("messages", [])
    if messaggi:
        ultimo = messaggi[-1]
        # Gestisci sia il caso in cui content è stringa sia lista
        if isinstance(ultimo.content, str):
            return ultimo.content
        elif isinstance(ultimo.content, list):
            # Prendi solo i blocchi di testo
            testi = [b["text"] for b in ultimo.content if isinstance(b, dict) and b.get("type") == "text"]
            return "\n".join(testi) if testi else str(ultimo.content)

    return "Nessuna risposta dall'agente."


def esegui_agente_stream(agente, messaggio: str, thread_id: str = "default"):
    """
    Come esegui_agente(), ma restituisce la risposta in streaming.
    Ideale per Streamlit.

    Parametri:
        agente:    l'agente creato con crea_agente()
        messaggio: il messaggio dell'utente
        thread_id: identificativo della conversazione

    Ritorna:
        Un generatore che produce pezzi di testo

    Esempio con Streamlit:
        with st.chat_message("assistant"):
            st.write_stream(esegui_agente_stream(agente, domanda))
    """
    config = {"configurable": {"thread_id": thread_id}}

    for event in agente.stream(
        {"messages": [{"role": "user", "content": messaggio}]},
        config=config,
        stream_mode="messages",
    ):
        # event è una tupla (messaggio, metadata)
        msg, metadata = event
        if hasattr(msg, "content") and msg.content and msg.type == "ai":
            # Il contenuto può arrivare come stringa o come lista di blocchi
            if isinstance(msg.content, str):
                yield msg.content
            elif isinstance(msg.content, list):
                for blocco in msg.content:
                    if isinstance(blocco, dict) and blocco.get("type") == "text":
                        yield blocco["text"]
                    elif isinstance(blocco, str):
                        yield blocco
