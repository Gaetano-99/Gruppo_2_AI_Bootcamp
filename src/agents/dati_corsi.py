"""
src/agents/dati_corsi.py
Knowledge base statica per l'agente di orientamento universitario (modalità Ospite).
"""

CATALOGO_CORSI = {
    "ingegneria": {
        "nome_completo": "Ingegneria (Varie Specializzazioni)",
        "descrizione": "I corsi di ingegneria forniscono solide basi matematiche, fisiche e metodologiche per progettare, realizzare e gestire sistemi e processi complessi.",
        "materie_principali": ["Analisi Matematica", "Fisica Generale", "Informatica", "Meccanica", "Elettrotecnica"],
        "sbocchi_lavorativi": ["Progettista", "Direttore Lavori", "Consulente Tecnico", "R&D", "Libera Professione"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_informatica": {
        "nome_completo": "Ingegneria Informatica",
        "descrizione": "Corso focalizzato sulla progettazione e sviluppo sia dell'hardware che del software, coprendo reti, sistemi operativi e architetture dei calcolatori.",
        "materie_principali": ["Programmazione", "Architettura degli Elaboratori", "Basi di Dati", "Reti di Calcolatori", "Ingegneria del Software"],
        "sbocchi_lavorativi": ["Sviluppatore Software", "Sistemista", "Progettista di Reti", "Analista Dati"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "informatica": {
        "nome_completo": "Informatica (Scienze MM.FF.NN.)",
        "descrizione": "Corso incentrato sugli aspetti teorici e applicativi del software, crittografia, intelligenza artificiale e teoria della computazione. A differenza di Ing. Informatica, ha meno focus sull'hardware e la fisica.",
        "materie_principali": ["Algoritmi e Strutture Dati", "Linguaggi di Programmazione", "Sistemi Operativi", "Basi di Dati", "Intelligenza Artificiale"],
        "sbocchi_lavorativi": ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", "Ricercatore"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "economia_e_commercio": {
        "nome_completo": "Economia e Commercio",
        "descrizione": "Fornisce competenze in ambito micro/macro economico, aziendale, giuridico e quantitativo, preparando a comprendere le dinamiche dei mercati e della gestione d'impresa.",
        "materie_principali": ["Microeconomia", "Macroeconomia", "Economia Aziendale", "Diritto Privato/Commerciale", "Statistica"],
        "sbocchi_lavorativi": ["Manager Aziendale", "Commercialista", "Consulente Finanziario", "Marketing Specialist", "Impiegato Bancario"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "matematica": {
        "nome_completo": "Matematica",
        "descrizione": "Punta alla formazione di una mentalità analitica e rigorosa, esplorando l'algebra, l'analisi, la geometria e le loro applicazioni in vari campi.",
        "materie_principali": ["Analisi Matematica", "Algebra Lineare", "Geometria", "Fisica Matematica", "Probabilità"],
        "sbocchi_lavorativi": ["Insegnante", "Ricercatore", "Data Analyst", "Attuario", "Analista Finanziario"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "fisica": {
        "nome_completo": "Fisica",
        "descrizione": "Studia le leggi fondamentali della natura attraverso metodi sperimentali, teorici e computazionali, dall'infinitamente piccolo (particelle) all'infinitamente grande (astrofisica).",
        "materie_principali": ["Fisica Classica", "Meccanica Quantistica", "Fisica Teorica", "Laboratorio di Fisica sperimentale", "Analisi Matematica"],
        "sbocchi_lavorativi": ["Ricercatore Accademico/Industriale", "Data Scientist", "Insegnante", "Esperto in tecnologie avanzate (ottica, materiali)"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_della_terra": {
        "nome_completo": "Scienze della Terra (Geologia)",
        "descrizione": "Corso dedicato allo studio del pianeta Terra, la sua evoluzione fisica, chimica e biologica, e l'interazione tra i processi interni e superficiali.",
        "materie_principali": ["Geologia", "Mineralogia", "Paleontologia", "Geofisica", "Geochimica"],
        "sbocchi_lavorativi": ["Geologo", "Consulente Ambientale", "Protezione Civile", "Ricercatore", "Tecnico per l'estrazione risorse"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    }
}
