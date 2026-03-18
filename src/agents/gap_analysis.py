"""
Modulo: gap_analysis.py
Responsabilità: Analizza le risposte errate di un tentativo quiz e identifica le lacune
dello studente, suggerendo gli argomenti e le sezioni da rivedere.

API pubblica:
    - analizza_gap(tentativo_id, studente_id) -> str
        Restituisce un report testuale con le lacune e i consigli di revisione.
    - salva_tentativo(quiz_id, studente_id, domande, risposte_studente) -> int
        Salva tentativi_quiz + risposte_domande, restituisce il tentativo_id.
    - calcola_punteggio(domande, risposte_studente) -> tuple[float, list[bool]]
        Calcola punteggio 0-100 e lista corrette/errate.
"""

from __future__ import annotations

import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db

try:
    from platform_sdk.llm import chiedi_con_contesto
except ImportError:
    from llm import chiedi_con_contesto


# ---------------------------------------------------------------------------
# Helpers interni
# ---------------------------------------------------------------------------

def calcola_punteggio(domande: list[dict], risposte_studente: dict[int, int]) -> tuple[float, list[bool]]:
    """
    Calcola punteggio (0-100) e lista corrette/errate per ogni domanda.

    domande:           lista di dict con 'indice_corretta' (int) o 'risposta_corretta' (str indice)
    risposte_studente: {indice_domanda (0-based): indice_opzione_selezionata}
    """
    if not domande:
        return 0.0, []

    corrette: list[bool] = []
    for i, d in enumerate(domande):
        corretta_raw = d.get("indice_corretta") if d.get("indice_corretta") is not None else d.get("risposta_corretta")
        try:
            corretta_idx = int(corretta_raw)
        except (TypeError, ValueError):
            corretta_idx = 0

        corrette.append(risposte_studente.get(i) == corretta_idx)

    punteggio = (sum(corrette) / len(domande)) * 100
    return punteggio, corrette


def salva_tentativo(
    quiz_id: int,
    studente_id: int,
    domande: list[dict],
    risposte_studente: dict[int, int],
) -> int:
    """
    Persiste il tentativo sul DB e restituisce il tentativo_id.

    domande:           lista ordinata di dict delle domande (con 'id' se provengono dal DB)
    risposte_studente: {indice_domanda (0-based): indice_opzione_selezionata}
    """
    punteggio, corrette = calcola_punteggio(domande, risposte_studente)

    # Raccoglie argomenti errati per aree_deboli_json
    aree_deboli: list[str] = []
    for i, (d, ok) in enumerate(zip(domande, corrette)):
        if not ok:
            testo_d = d.get("testo") or d.get("domanda") or ""
            aree_deboli.append(testo_d[:120])

    tentativo_id = db.inserisci("tentativi_quiz", {
        "quiz_id": quiz_id,
        "studente_id": studente_id,
        "punteggio": round(punteggio, 1),
        "aree_deboli_json": json.dumps(aree_deboli, ensure_ascii=False),
        "completato": 1,
    })

    # Salva le singole risposte
    for i, (d, ok) in enumerate(zip(domande, corrette)):
        domanda_id = d.get("id")  # None se domanda inline (Caso A)
        if domanda_id is None:
            continue  # Domande inline: registriamo solo il tentativo aggregato

        opzioni_raw = d.get("opzioni_json") or json.dumps(d.get("opzioni") or [])
        try:
            opzioni = json.loads(opzioni_raw) if isinstance(opzioni_raw, str) else opzioni_raw
        except Exception:
            opzioni = []

        idx_sel = risposte_studente.get(i)
        risposta_testo = opzioni[idx_sel] if (idx_sel is not None and 0 <= idx_sel < len(opzioni)) else None

        db.inserisci("risposte_domande", {
            "tentativo_id": tentativo_id,
            "domanda_id": domanda_id,
            "risposta_data": risposta_testo,
            "corretta": 1 if ok else 0,
        })

    return tentativo_id


# ---------------------------------------------------------------------------
# Analisi gap con LLM
# ---------------------------------------------------------------------------

def analizza_gap(tentativo_id: int, studente_id: int) -> str:
    """
    Analizza le risposte errate del tentativo e restituisce un report personalizzato.
    Usa i chunk_id delle domande (se presenti) per identificare le sezioni da rivedere.
    """
    # Risposte errate con metadati domanda e chunk
    risposte_errate = db.esegui(
        """
        SELECT
            dq.testo           AS domanda,
            dq.spiegazione,
            mc.titolo_sezione,
            mc.sommario,
            mc.argomenti_chiave
        FROM risposte_domande rd
        JOIN domande_quiz dq ON rd.domanda_id = dq.id
        LEFT JOIN materiali_chunks mc ON dq.chunk_id = mc.id
        WHERE rd.tentativo_id = ? AND rd.corretta = 0
        """,
        [tentativo_id],
    )

    if not risposte_errate:
        return (
            "**Ottimo lavoro! 🎉** Non hai commesso nessun errore in questo quiz. "
            "Sei pronto/a per passare all'argomento successivo!"
        )

    # Raccoglie argomenti e sezioni dagli errori
    argomenti: set[str] = set()
    sezioni: list[str] = []
    domande_errate: list[str] = []

    for r in risposte_errate:
        domande_errate.append(r["domanda"])
        if r.get("argomenti_chiave"):
            try:
                for a in json.loads(r["argomenti_chiave"]):
                    argomenti.add(a)
            except Exception:
                pass
        if r.get("titolo_sezione") and r["titolo_sezione"] not in sezioni:
            sezioni.append(r["titolo_sezione"])

    # Tentativo con punteggio per il contesto
    tentativo = db.trova_uno("tentativi_quiz", {"id": tentativo_id})
    punteggio = tentativo.get("punteggio", 0) if tentativo else 0
    n_errate = len(domande_errate)

    contesto = f"""Lo studente ha completato un quiz con punteggio {punteggio:.0f}/100.
Ha sbagliato {n_errate} domanda/e:
{chr(10).join(f'  - {d}' for d in domande_errate)}

Argomenti chiave delle sezioni con errori: {', '.join(argomenti) if argomenti else 'Non specificati'}
Sezioni del materiale da rivedere: {', '.join(sezioni) if sezioni else 'Non disponibili'}"""

    # Recupera i titoli delle sezioni disponibili nel corso per vincolare i suggerimenti
    sezioni_corso: list[str] = []
    if tentativo:
        quiz_row = db.trova_uno("quiz", {"id": tentativo.get("quiz_id")})
        if quiz_row and quiz_row.get("corso_id"):
            rows_sez = db.esegui(
                "SELECT DISTINCT titolo_sezione FROM materiali_chunks "
                "WHERE corso_id = ? AND titolo_sezione IS NOT NULL",
                [quiz_row["corso_id"]],
            )
            sezioni_corso = [r["titolo_sezione"] for r in rows_sez if r.get("titolo_sezione")]

    sezioni_disponibili_str = (
        "Sezioni disponibili nel materiale del corso: " + ", ".join(sezioni_corso)
        if sezioni_corso
        else "Non sono disponibili dettagli sulle sezioni del corso."
    )

    istruzioni = (
        "Sei Lea, il tutor di LearnAI. Analizza i risultati del quiz dello studente.\n"
        "IMPORTANTE: Lo studente NON può rispondere direttamente a questa analisi, "
        "quindi NON fare domande e NON chiedere conferme.\n"
        f"{sezioni_disponibili_str}\n"
        "Struttura la risposta così:\n"
        "1. Elenca in modo chiaro le aree di miglioramento (argomenti non padroneggiati).\n"
        "2. Per ogni area, spiega brevemente cosa rivedere e perché è importante.\n"
        "3. Se ci sono sezioni specifiche del materiale, citale.\n"
        "4. Suggerisci 2-3 domande concrete che lo studente può fare a Lea in chat "
        "per approfondire le lacune. IMPORTANTE: le domande devono essere basate SOLO "
        "sugli argomenti e le sezioni effettivamente presenti nel materiale del corso. "
        "NON suggerire domande su dati, statistiche o fonti specifiche che non sono "
        "nel materiale. Usa formule come 'Puoi spiegarmi meglio [argomento dalla sezione X]...', "
        "'Fammi un riassunto di [sezione del materiale]...', "
        "'Generami un nuovo quiz su [argomento del corso]...'.\n"
        "5. Concludi con un breve incoraggiamento.\n"
        "Usa un tono empatico e motivante. Usa elenchi puntati. Massimo 250 parole."
    )

    try:
        return chiedi_con_contesto(
            domanda="Analizza le mie lacune e dimmi cosa rivedere",
            contesto=contesto,
            istruzioni=istruzioni,
        )
    except Exception as e:
        # Fallback senza LLM
        righe = [f"**Punteggio: {punteggio:.0f}/100** — {n_errate} errore/i rilevato/i.\n"]
        if argomenti:
            righe.append("**Argomenti da rivedere:**")
            for a in sorted(argomenti):
                righe.append(f"- {a}")
        if sezioni:
            righe.append("\n**Sezioni del materiale:**")
            for s in sezioni:
                righe.append(f"- {s}")
        righe.append("\nParla con Lea per un piano di recupero personalizzato!")
        return "\n".join(righe)
