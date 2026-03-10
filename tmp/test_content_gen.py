"""Test strutturale di content_gen.py — verifica modelli, stato e grafo."""
import sys, os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

print("=" * 60)
print("TEST 1: Import dei modelli Pydantic")
try:
    from src.agents.content_gen import Paragrafo, Capitolo, StrutturaCorso
    print("  OK — Paragrafo, Capitolo, StrutturaCorso importati")
except ImportError as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

print()
print("TEST 2: Verifica che i vecchi modelli NON esistano più")
try:
    from src.agents.content_gen import DomandaQuiz
    print("  FAIL — DomandaQuiz esiste ancora!")
except ImportError:
    print("  OK — DomandaQuiz rimosso correttamente")

try:
    from src.agents.content_gen import QuizGenerato
    print("  FAIL — QuizGenerato esiste ancora!")
except ImportError:
    print("  OK — QuizGenerato rimosso correttamente")

try:
    from src.agents.content_gen import FlashcardGenerata
    print("  FAIL — FlashcardGenerata esiste ancora!")
except ImportError:
    print("  OK — FlashcardGenerata rimosso correttamente")

print()
print("TEST 3: Istanziazione modelli Pydantic con dati di esempio")
try:
    corso = StrutturaCorso(
        titolo_corso="Introduzione a Python",
        descrizione_breve="Un corso rapido per imparare le basi.",
        durata_stimata_minuti=120,
        capitoli=[
            Capitolo(
                id_capitolo="cap_01",
                titolo="Le basi: Variabili",
                ordine=1,
                paragrafi=[
                    Paragrafo(
                        id_paragrafo="par_01_01",
                        titolo="Cosa sono le variabili",
                        testo="Le variabili sono dei contenitori per memorizzare dati..."
                    ),
                    Paragrafo(
                        id_paragrafo="par_01_02",
                        titolo="Tipi di dato",
                        testo="Python supporta diversi tipi: int, float, str, bool..."
                    ),
                ],
            ),
        ],
    )
    d = corso.model_dump()
    assert d["titolo_corso"] == "Introduzione a Python"
    assert len(d["capitoli"]) == 1
    assert len(d["capitoli"][0]["paragrafi"]) == 2
    assert d["capitoli"][0]["paragrafi"][0]["id_paragrafo"] == "par_01_01"
    print("  OK — StrutturaCorso istanziata e serializzata correttamente")
    print(f"       JSON keys: {list(d.keys())}")
except Exception as e:
    print(f"  FAIL — {e}")

print()
print("TEST 4: Verifica ContentGenState (campi)")
try:
    from src.agents.content_gen import ContentGenState
    hints = ContentGenState.__annotations__
    
    assert "corso_id" in hints, "Manca corso_id"
    assert "argomento_richiesto" in hints, "Manca argomento_richiesto"
    assert "struttura_corso_generata" in hints, "Manca struttura_corso_generata"
    assert "chunk_ids_utilizzati" in hints, "Manca chunk_ids_utilizzati"
    assert "errore" in hints, "Manca errore"
    
    assert "tipo_strumento" not in hints, "tipo_strumento doveva essere rimosso!"
    assert "strumenti_studio_generati" not in hints, "strumenti_studio_generati doveva essere rimosso!"
    assert "lezione_generata" not in hints, "lezione_generata doveva essere rimosso!"
    
    print("  OK — ContentGenState ha i campi corretti")
    print(f"       Campi: {list(hints.keys())}")
except AssertionError as e:
    print(f"  FAIL — {e}")

print()
print("TEST 5: Costruzione e ispezione del grafo")
try:
    from src.agents.content_gen import crea_agente_content_gen
    agente = crea_agente_content_gen()
    
    nodi = list(agente.get_graph().nodes.keys())
    # LangGraph aggiunge __start__ e __end__ automaticamente
    nodi_utente = [n for n in nodi if not n.startswith("__")]
    
    assert "recupera_chunks" in nodi_utente, "Manca nodo recupera_chunks"
    assert "genera_struttura_corso" in nodi_utente, "Manca nodo genera_struttura_corso"
    assert "salva_risultati" in nodi_utente, "Manca nodo salva_risultati"
    assert "genera_strumenti_studio" not in nodi_utente, "genera_strumenti_studio doveva essere rimosso!"
    assert "genera_lezione" not in nodi_utente, "genera_lezione doveva essere rinominato!"
    
    print(f"  OK — Grafo compilato con {len(nodi_utente)} nodi: {nodi_utente}")
except Exception as e:
    print(f"  FAIL — {e}")

print()
print("TEST 6: Verifica firma esegui_generazione (senza tipo_strumento)")
try:
    import inspect
    from src.agents.content_gen import esegui_generazione
    sig = inspect.signature(esegui_generazione)
    params = list(sig.parameters.keys())
    
    assert "tipo_strumento" not in params, "tipo_strumento doveva essere rimosso dalla firma!"
    assert "agente" in params
    assert "corso_id" in params
    assert "argomento_richiesto" in params
    
    print(f"  OK — Firma: esegui_generazione({', '.join(params)})")
except AssertionError as e:
    print(f"  FAIL — {e}")

print()
print("=" * 60)
print("TUTTI I TEST COMPLETATI")
