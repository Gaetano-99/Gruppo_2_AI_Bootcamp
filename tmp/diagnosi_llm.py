"""Diagnostica: verifica che la catena config → llm funzioni correttamente."""
import sys, os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

print("=" * 60)
print("STEP 1: Import config")
try:
    import config
    print(f"  OK — AWS_DEFAULT_REGION = {config.AWS_DEFAULT_REGION}")
    print(f"  OK — BEDROCK_MODEL_ID   = {config.BEDROCK_MODEL_ID}")
    print(f"  OK — AWS_ACCESS_KEY_ID  = {'SET' if config.AWS_ACCESS_KEY_ID else 'MANCANTE!'}")
    print(f"  OK — AWS_SECRET_ACCESS_KEY = {'SET' if config.AWS_SECRET_ACCESS_KEY else 'MANCANTE!'}")
except Exception as e:
    print(f"  ERRORE: {e}")

print()
print("STEP 2: Import platform_sdk.llm")
try:
    from platform_sdk.llm import get_llm, chat
    print("  OK — importati get_llm e chat")
except Exception as e:
    print(f"  ERRORE: {e}")

print()
print("STEP 3: Crea istanza LLM")
try:
    llm = get_llm()
    print(f"  OK — tipo: {type(llm)}")
except Exception as e:
    print(f"  ERRORE: {e}")

print()
print("STEP 4: Invoca llm.invoke() con un messaggio semplice")
try:
    from langchain_core.messages import HumanMessage
    risposta = llm.invoke([HumanMessage(content="Rispondi solo: OK")])
    print(f"  OK — risposta: {risposta.content[:100]}")
except Exception as e:
    print(f"  ERRORE: {type(e).__name__}: {e}")

print()
print("STEP 5: Invoca chat() con un messaggio semplice")
try:
    risposta = chat([{"role": "user", "content": "Rispondi solo: OK"}], system_prompt="Sei un assistente.")
    print(f"  OK — risposta: {risposta[:100]}")
except Exception as e:
    print(f"  ERRORE: {type(e).__name__}: {e}")

print()
print("=" * 60)
print("DIAGNOSTICA COMPLETATA")
