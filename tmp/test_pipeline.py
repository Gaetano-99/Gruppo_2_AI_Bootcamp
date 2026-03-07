"""
Test CLI End-to-End — Pipeline completa backend LearnAI.

Testa in sequenza:
  1. Database: inizializzazione e stato
  2. Ingestione documento: chunking da testo simulato
  3. RAG: retrieval dei chunk per argomento
  4. Agente Teorico: generazione StrutturaCorso JSON (richiede AWS Bedrock)

Uso:
  python tmp\test_pipeline.py           # Esegue step 1-3 (senza LLM)
  python tmp\test_pipeline.py --llm     # Esegue step 1-4 (con chiamata Bedrock)
"""
import sys, os, json

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

USA_LLM = "--llm" in sys.argv


def separatore(titolo):
    print(f"\n{'='*60}")
    print(f"  {titolo}")
    print(f"{'='*60}\n")


# ──────────────────────────────────────────────────────────────
# STEP 1: Database
# ──────────────────────────────────────────────────────────────
separatore("STEP 1: Database — Init e stato")

from platform_sdk.database import db

try:
    db.init()
    print("  OK — db.init() completato")
except Exception as e:
    print(f"  WARN — db.init() ha dato errore (potrebbe essere già inizializzato): {e}")

# Conta alcune tabelle chiave
tabelle_check = ["users", "corsi_universitari", "materiali_didattici", "materiali_chunks"]
for tabella in tabelle_check:
    try:
        n = db.conta(tabella)
        print(f"  {tabella}: {n} righe")
    except Exception as e:
        print(f"  {tabella}: ERRORE — {e}")

# Verifica che esista almeno un corso
corsi = db.trova_tutti("corsi_universitari", limite=3)
if corsi:
    print(f"\n  Corsi trovati:")
    for c in corsi:
        print(f"    ID={c['id']} | {c.get('nome', c.get('titolo', '?'))}")
    CORSO_ID_TEST = corsi[0]["id"]
else:
    print("  WARN — Nessun corso trovato, uso corso_id=1 di default")
    CORSO_ID_TEST = 1


# ──────────────────────────────────────────────────────────────
# STEP 2: Ingestione documento (chunking diretto, senza Streamlit)
# ──────────────────────────────────────────────────────────────
separatore("STEP 2: Ingestione — Chunking testo simulato")

TESTO_SIMULATO = """
Introduzione alla Programmazione in Python

Python è un linguaggio di programmazione ad alto livello, interpretato e general-purpose.
Creato da Guido van Rossum nel 1991, Python enfatizza la leggibilità del codice e la
semplicità sintattica. È ampiamente usato in data science, sviluppo web, automazione e AI.

Le Variabili in Python

Le variabili in Python sono contenitori per memorizzare valori. A differenza di altri
linguaggi, Python utilizza il typing dinamico: non è necessario dichiarare il tipo.
Esempio: x = 10 crea una variabile intera. nome = "Mario" crea una stringa.
Le variabili possono cambiare tipo durante l'esecuzione del programma.

Le Strutture Dati Fondamentali

Python offre quattro strutture dati principali: liste, tuple, dizionari e set.
Le liste sono sequenze ordinate e mutabili: numeri = [1, 2, 3].
I dizionari sono coppie chiave-valore: persona = {"nome": "Mario", "eta": 30}.
Le tuple sono come le liste, ma immutabili: coordinate = (10, 20).
I set sono insiemi non ordinati di elementi unici: unici = {1, 2, 3}.

I Cicli e le Condizioni

I costrutti condizionali (if/elif/else) permettono di eseguire codice in base a condizioni.
I cicli for iterano su sequenze: for i in range(10): print(i).
I cicli while ripetono finché una condizione è vera: while x > 0: x -= 1.
La parola chiave break interrompe il ciclo, continue salta all'iterazione successiva.

Le Funzioni in Python

Le funzioni sono blocchi di codice riutilizzabili definiti con la parola chiave def.
Esempio: def saluta(nome): return f"Ciao {nome}!".
Le funzioni possono avere parametri con valori predefiniti e possono restituire valori.
Python supporta anche le funzioni lambda per operazioni semplici: quadrato = lambda x: x**2.
"""

from src.tools.document_processor import _crea_e_salva_chunks

# Inserisci un materiale didattico di test direttamente
DOCENTE_ID_TEST = 1
materiale_id = db.inserisci(
    "materiali_didattici",
    {
        "corso_universitario_id": CORSO_ID_TEST,
        "docente_id": DOCENTE_ID_TEST,
        "titolo": "[TEST-CLI] Introduzione Python",
        "tipo": "dispensa",
        "s3_key": "test/cli/intro_python.txt",
        "testo_estratto": TESTO_SIMULATO,
        "is_processed": 0,
    },
)
print(f"  Materiale inserito con ID: {materiale_id}")

# Chunking
chunk_ids = _crea_e_salva_chunks(
    testo=TESTO_SIMULATO,
    materiale_id=materiale_id,
    corso_universitario_id=CORSO_ID_TEST,
)
print(f"  Chunks creati: {len(chunk_ids)} (IDs: {chunk_ids})")

# Marca come processato
db.aggiorna("materiali_didattici", {"id": materiale_id}, {"is_processed": 1})
print(f"  Materiale marcato come processato")

# Verifica chunks salvati
for cid in chunk_ids[:2]:  # mostra solo i primi 2
    chunk = db.trova_uno("materiali_chunks", {"id": cid})
    print(f"\n  Chunk ID={cid}:")
    print(f"    Testo (primi 120 char): {chunk['testo'][:120]}...")
    print(f"    Token stimati: {chunk['n_token']}")


# ──────────────────────────────────────────────────────────────
# STEP 3: RAG — Retrieval semantico
# ──────────────────────────────────────────────────────────────
separatore("STEP 3: RAG — Retrieval chunk per argomento")

from src.tools.rag_engine import cerca_chunk_rilevanti, formatta_contesto_rag, conta_chunk_corso

n_chunks_corso = conta_chunk_corso(CORSO_ID_TEST)
print(f"  Chunks totali per corso {CORSO_ID_TEST}: {n_chunks_corso}")

# Test retrieval con query specifica
query_test = "variabili e tipi di dato in Python"
chunks_trovati = cerca_chunk_rilevanti(corso_id=CORSO_ID_TEST, query=query_test, top_k=3)

print(f"\n  Query: '{query_test}'")
print(f"  Chunks trovati: {len(chunks_trovati)}")

for i, c in enumerate(chunks_trovati):
    print(f"\n  [{i+1}] Chunk ID={c['id']} | Score={c.get('score_rilevanza', 0)}")
    print(f"      Parole trovate: {c.get('parole_trovate', [])}")
    print(f"      Testo (primi 100 char): {c['testo'][:100]}...")

# Mostra il contesto formattato come lo vedrebbe l'LLM
contesto = formatta_contesto_rag(chunks_trovati)
print(f"\n  Contesto RAG formattato ({len(contesto)} caratteri):")
print(f"  (prime 300 char):")
print(f"  {contesto[:300]}...")


# ──────────────────────────────────────────────────────────────
# STEP 4: Agente Teorico — Generazione StrutturaCorso (solo con --llm)
# ──────────────────────────────────────────────────────────────
if USA_LLM:
    separatore("STEP 4: Agente Teorico — Generazione StrutturaCorso via Bedrock")

    from src.agents.content_gen import crea_agente_content_gen, esegui_generazione

    agente = crea_agente_content_gen()
    print("  Grafo compilato. Invoco il LLM (potrebbe richiedere 10-30 secondi)...")

    stato_finale = esegui_generazione(
        agente=agente,
        corso_id=CORSO_ID_TEST,
        argomento_richiesto="Introduzione alla programmazione Python",
        docente_id=DOCENTE_ID_TEST,
        is_corso_docente=True,
    )

    if stato_finale.get("errore"):
        print(f"\n  ERRORE: {stato_finale['errore']}")
    else:
        struttura = stato_finale["struttura_corso_generata"]
        print(f"\n  SUCCESSO! StrutturaCorso generata:")
        print(f"    Titolo: {struttura.get('titolo_corso')}")
        print(f"    Descrizione: {struttura.get('descrizione_breve')}")
        print(f"    Durata stimata: {struttura.get('durata_stimata_minuti')} minuti")
        print(f"    N. capitoli: {len(struttura.get('capitoli', []))}")

        for cap in struttura.get("capitoli", []):
            print(f"\n    cap: {cap['id_capitolo']} - {cap['titolo']} (ordine: {cap['ordine']})")
            for par in cap.get("paragrafi", []):
                print(f"       par: {par['id_paragrafo']} - {par['titolo']}")
                print(f"          {par['testo'][:80]}...")

        print(f"\n    Chunk IDs utilizzati: {stato_finale['chunk_ids_utilizzati']}")

        # Verifica salvataggio normalizzato nelle tabelle relazionali
        separatore("STEP 5: Verifica salvataggio normalizzato nel DB")

        piano = db.esegui(
            "SELECT * FROM piani_personalizzati WHERE is_corso_docente = 1 ORDER BY id DESC LIMIT 1"
        )
        if piano:
            p = piano[0]
            print(f"  piani_personalizzati:")
            print(f"    ID={p['id']} | Titolo={p['titolo']} | tipo={p['tipo']} | is_corso_docente={p['is_corso_docente']}")

            capitoli_db = db.trova_tutti("piano_capitoli", {"piano_id": p["id"]}, ordine="ordine ASC")
            print(f"\n  piano_capitoli: {len(capitoli_db)} record")
            for cap_db in capitoli_db:
                print(f"    ID={cap_db['id']} | {cap_db['titolo']} | ordine={cap_db['ordine']}")

                paragrafi_db = db.trova_tutti("piano_paragrafi", {"capitolo_id": cap_db["id"]})
                for par_db in paragrafi_db:
                    contenuto = db.trova_uno("piano_contenuti", {"paragrafo_id": par_db["id"]})
                    testo_preview = (contenuto["contenuto_json"] or "")[:60] if contenuto else "(vuoto)"
                    print(f"      par ID={par_db['id']} | {par_db['titolo']} | testo: {testo_preview}...")
        else:
            print("  ERRORE: nessun piano trovato in DB!")

        # Salva il JSON per ispezione
        out_path = os.path.join(_ROOT, "tmp", "output_struttura_corso.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(struttura, f, ensure_ascii=False, indent=2)
        print(f"\n    JSON completo salvato in: {out_path}")
else:
    separatore("STEP 4: SKIPPED (usa --llm per testare la generazione Bedrock)")
    print("  Esegui: python tmp\\test_pipeline.py --llm")


# ──────────────────────────────────────────────────────────────
# Pulizia dati di test
# ──────────────────────────────────────────────────────────────
separatore("PULIZIA - Rimozione dati di test")

n_chunks_rimossi = db.elimina("materiali_chunks", {"materiale_id": materiale_id})
n_mat_rimossi = db.elimina("materiali_didattici", {"id": materiale_id})
print(f"  Rimossi: {n_chunks_rimossi} chunks, {n_mat_rimossi} materiale")

# Rimuovi il piano generato (CASCADE elimina capitoli, paragrafi, contenuti)
if USA_LLM:
    piani_test = db.esegui(
        "SELECT id FROM piani_personalizzati WHERE is_corso_docente = 1 ORDER BY id DESC LIMIT 1"
    )
    if piani_test:
        piano_id_del = piani_test[0]["id"]
        # CASCADE: elimina piano_capitoli -> piano_paragrafi -> piano_contenuti
        db.elimina("piani_personalizzati", {"id": piano_id_del})
        print(f"  Rimosso piano test ID={piano_id_del} (+ capitoli/paragrafi/contenuti a cascata)")

print("\n" + "=" * 60)
print("  PIPELINE COMPLETATA CON SUCCESSO")
print("=" * 60)

