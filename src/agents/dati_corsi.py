"""
src/agents/dati_corsi.py
Knowledge base statica per l'agente di orientamento universitario (modalità Ospite).
Dati estesi e aggiornati sull'offerta formativa dell'Università Federico II di Napoli.
Fonte: unina.it, AlmaLaurea, ammissione.it — A.A. 2025/2026
13 Aree Didattiche | 172+ corsi tra triennali, magistrali e ciclo unico
"""

CATALOGO_CORSI = {

    # =========================================================
    # AREA 1 — AGRARIA
    # =========================================================
    "scienze_agrarie_forestali_ambientali": {
        "nome_completo": "Scienze Agrarie, Forestali e Ambientali",
        "area": "Agraria",
        "tipo": "Triennale (L-25)",
        "descrizione": "Formazione sulle tecniche agronomiche, zootecniche e di gestione forestale e ambientale in ottica di sostenibilità.",
        "materie_principali": ["Agronomia Generale", "Chimica Agraria", "Patologia Vegetale", "Zootecnica", "Economia Agraria"],
        "sbocchi_lavorativi": ["Agronomo", "Consulente agricolo", "Tecnico forestale", "Ente pubblico ambientale"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_gastronomiche_mediterranee": {
        "nome_completo": "Scienze Gastronomiche Mediterranee",
        "area": "Agraria",
        "tipo": "Triennale (L/GASTR)",
        "descrizione": "Studio scientifico e culturale della gastronomia mediterranea, filiera alimentare, territorio e qualità dei prodotti tipici.",
        "materie_principali": ["Chimica degli Alimenti", "Storia della Gastronomia", "Nutrizione", "Marketing Agroalimentare", "Enogastronomia"],
        "sbocchi_lavorativi": ["Esperto gastronomico", "Food journalist", "Responsabile qualità alimentare", "Consulente ristorativo"],
        "durata": "3 anni (Triennale)"
    },
    "tecnologie_alimentari": {
        "nome_completo": "Tecnologie Alimentari",
        "area": "Agraria",
        "tipo": "Triennale (L-26)",
        "descrizione": "Formazione sulle tecniche di produzione, trasformazione e controllo qualità nell'industria agroalimentare.",
        "materie_principali": ["Tecnologie Alimentari", "Microbiologia degli Alimenti", "Impianti Industriali", "Chimica degli Alimenti", "Legislazione Alimentare"],
        "sbocchi_lavorativi": ["Tecnologo alimentare", "Responsabile produzione industria alimentare", "Controllo qualità", "Ricerca e sviluppo"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "viticoltura_enologia": {
        "nome_completo": "Viticoltura ed Enologia",
        "area": "Agraria",
        "tipo": "Triennale (L-25)",
        "descrizione": "Percorso professionalizzante sulla coltivazione della vite, produzione del vino e gestione delle cantine. Sede: Avellino.",
        "materie_principali": ["Viticoltura", "Enologia", "Analisi Sensoriale", "Chimica del Vino", "Marketing del Vino"],
        "sbocchi_lavorativi": ["Enologo", "Agronomo vitivinicolo", "Direttore tecnico di cantina", "Wine consultant"],
        "durata": "3 anni (Triennale)"
    },
    "scienze_tecnologie_agrarie_m": {
        "nome_completo": "Scienze e Tecnologie Agrarie (Magistrale)",
        "area": "Agraria",
        "tipo": "Magistrale (LM-69)",
        "descrizione": "Approfondimento avanzato su produzione vegetale sostenibile, biotecnologie vegetali e gestione delle risorse naturali.",
        "materie_principali": ["Miglioramento Genetico Vegetale", "Agroecologia", "Biotecnologie Agrarie", "Gestione del Suolo"],
        "sbocchi_lavorativi": ["Ricercatore", "Agronomo senior", "Consulente per enti europei", "Gestione parchi naturali"],
        "durata": "2 anni (Magistrale)"
    },
    "scienze_tecnologie_alimentari_m": {
        "nome_completo": "Scienze e Tecnologie Alimentari (Magistrale)",
        "area": "Agraria",
        "tipo": "Magistrale (LM-70)",
        "descrizione": "Formazione avanzata sulla scienza degli alimenti, tecnologie di processo e innovazione nel settore agroalimentare.",
        "materie_principali": ["Scienza degli Alimenti", "Biotecnologie Alimentari", "Packaging e Shelf-life", "Qualità e Sicurezza Alimentare"],
        "sbocchi_lavorativi": ["Direttore R&D industria alimentare", "Food scientist", "Consulente qualità", "Ente di controllo HACCP"],
        "durata": "2 anni (Magistrale)"
    },
    "scienza_alimenti_nutrizione_m": {
        "nome_completo": "Scienza degli Alimenti e Nutrizione (Magistrale)",
        "area": "Agraria",
        "tipo": "Magistrale (LM-61)",
        "descrizione": "Integra alimentazione, nutrizione umana e scienze dell'alimento per formare esperti nella prevenzione e promozione della salute.",
        "materie_principali": ["Nutrizione Clinica", "Scienze degli Alimenti Funzionali", "Dietetica Applicata", "Nutraceutica"],
        "sbocchi_lavorativi": ["Nutrizionista (in team medico)", "Consulente nutraceutico", "Tecnologo alimenti funzionali"],
        "durata": "2 anni (Magistrale)"
    },
    "scienze_forestali_ambientali_m": {
        "nome_completo": "Scienze Forestali e Ambientali (Magistrale)",
        "area": "Agraria",
        "tipo": "Magistrale (LM-73)",
        "descrizione": "Gestione avanzata delle risorse forestali, pianificazione territoriale e tutela degli ecosistemi.",
        "materie_principali": ["Selvicoltura Avanzata", "Pianificazione Forestale", "Ecologia del Paesaggio", "Gestione Fauna Selvatica"],
        "sbocchi_lavorativi": ["Dottore Forestale", "Consulente ambientale", "Enti parco nazionali", "Protezione civile"],
        "durata": "2 anni (Magistrale)"
    },

    # =========================================================
    # AREA 2 — ARCHITETTURA
    # =========================================================
    "architettura_ciclo_unico": {
        "nome_completo": "Architettura (Ciclo Unico)",
        "area": "Architettura",
        "tipo": "Magistrale a Ciclo Unico (LM-4 C.U.) — Accesso programmato nazionale",
        "descrizione": "Percorso abilitante alla professione di architetto: progettazione architettonica, urbanistica, restauro e costruzione sostenibile.",
        "materie_principali": ["Progettazione Architettonica", "Storia dell'Architettura", "Tecnica delle Costruzioni", "Urbanistica", "Restauro"],
        "sbocchi_lavorativi": ["Architetto (libera professione)", "Progettista urbanista", "Restauratore", "Dirigente in enti pubblici"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "scienze_architettura": {
        "nome_completo": "Scienze dell'Architettura",
        "area": "Architettura",
        "tipo": "Triennale (L-17)",
        "descrizione": "Formazione di base su progettazione, storia e tecnologia dell'architettura. Propedeutica alla magistrale.",
        "materie_principali": ["Fondamenti di Progettazione", "Matematica", "Fisica Tecnica", "Storia dell'Architettura", "Disegno Architettonico"],
        "sbocchi_lavorativi": ["Tecnico edile", "Collaboratore studi di architettura", "Accesso a magistrale LM-4"],
        "durata": "3 anni (Triennale)"
    },
    "design_comunita": {
        "nome_completo": "Design per la Comunità",
        "area": "Architettura",
        "tipo": "Triennale (L-4) — Accesso programmato locale",
        "descrizione": "Progettazione di prodotti, servizi e sistemi orientati alle persone e alle comunità. Design strategico e sostenibile.",
        "materie_principali": ["Design del Prodotto", "Design dei Servizi", "Human-Centered Design", "Storia del Design", "Ergonomia"],
        "sbocchi_lavorativi": ["Designer industriale", "UX/Service designer", "Product designer", "Consulente di innovazione"],
        "durata": "3 anni (Triennale)"
    },
    "sviluppo_sostenibile_reti_territoriali": {
        "nome_completo": "Sviluppo Sostenibile e Reti Territoriali",
        "area": "Architettura",
        "tipo": "Triennale (L-21)",
        "descrizione": "Pianificazione territoriale e paesaggistica in ottica di sviluppo sostenibile e resilienza urbana.",
        "materie_principali": ["Urbanistica", "GIS e Cartografia", "Economia del Territorio", "Politiche Ambientali", "Sostenibilità Urbana"],
        "sbocchi_lavorativi": ["Pianificatore territoriale", "Urban planner", "Consulente enti locali", "Esperto sviluppo sostenibile"],
        "durata": "3 anni (Triennale)"
    },
    "pianificazione_territoriale_m": {
        "nome_completo": "Pianificazione Territoriale, Urbanistica e Paesaggistico-Ambientale (Magistrale)",
        "area": "Architettura",
        "tipo": "Magistrale (LM-48)",
        "descrizione": "Formazione avanzata per la gestione sostenibile del territorio, della città e del paesaggio.",
        "materie_principali": ["Progettazione Urbana Avanzata", "Politiche Territoriali", "Valutazione Ambientale Strategica", "Smart City"],
        "sbocchi_lavorativi": ["Pianificatore senior", "Esperto politiche europee territoriali", "Ricercatore urbano"],
        "durata": "2 anni (Magistrale)"
    },

    # =========================================================
    # AREA 3 — BIOTECNOLOGIE DELLA SALUTE
    # =========================================================
    "biotecnologie_salute": {
        "nome_completo": "Biotecnologie per la Salute",
        "area": "Biotecnologie della Salute",
        "tipo": "Triennale (L-2) — Accesso programmato locale",
        "descrizione": "Applicazione delle biotecnologie in ambito medico e farmaceutico: diagnosi, terapia genica e sviluppo di farmaci biologici.",
        "materie_principali": ["Biologia Molecolare", "Biochimica", "Genetica", "Microbiologia", "Biologia Cellulare"],
        "sbocchi_lavorativi": ["Biotecnologo in R&D farmaceutico", "Diagnostica molecolare", "Ricercatore in IRCCS", "Accesso a magistrale LM-9"],
        "durata": "3 anni (Triennale)"
    },
    "biotecnologie_molecolari_industriali": {
        "nome_completo": "Biotecnologie Molecolari e Industriali",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-2) — Accesso programmato locale",
        "descrizione": "Biotecnologie applicate ai processi industriali, fermentazione, bioreattori e produzione di molecole biologiche.",
        "materie_principali": ["Microbiologia Industriale", "Biochimica Industriale", "Bioreattori", "Ingegneria Genetica", "Bioinformatica"],
        "sbocchi_lavorativi": ["Biotecnologo industriale", "Quality assurance industria bio-farmaceutica", "Ricercatore"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 4 — ECONOMIA
    # =========================================================
    "economia_aziendale": {
        "nome_completo": "Economia Aziendale",
        "area": "Economia",
        "tipo": "Triennale (L-18)",
        "descrizione": "Fondamenti di gestione aziendale, contabilità, finanza d'impresa e strategia organizzativa.",
        "materie_principali": ["Economia Aziendale", "Ragioneria", "Diritto Privato e Commerciale", "Statistica", "Marketing"],
        "sbocchi_lavorativi": ["Manager", "Commercialista", "Controller", "Analista finanziario", "Consulente aziendale"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "economia_imprese_finanziarie": {
        "nome_completo": "Economia delle Imprese Finanziarie",
        "area": "Economia",
        "tipo": "Triennale (L-18)",
        "descrizione": "Formazione specialistica in banca, assicurazioni e mercati finanziari, con focus su risk management e finanza d'impresa.",
        "materie_principali": ["Economia degli Intermediari Finanziari", "Matematica Finanziaria", "Diritto Bancario", "Statistica", "Mercati Finanziari"],
        "sbocchi_lavorativi": ["Analista creditizio", "Risk manager", "Wealth manager", "Assicuratore", "Gestore portafoglio"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "economia_commercio": {
        "nome_completo": "Economia e Commercio",
        "area": "Economia",
        "tipo": "Triennale (L-33)",
        "descrizione": "Formazione in micro e macroeconomia, econometria, economia internazionale e politiche pubbliche.",
        "materie_principali": ["Microeconomia", "Macroeconomia", "Statistica Economica", "Econometria", "Economia Internazionale"],
        "sbocchi_lavorativi": ["Economista", "Analista policy", "Ricercatore", "Enti internazionali", "Pubblica amministrazione"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "hospitality_management": {
        "nome_completo": "Hospitality Management",
        "area": "Economia",
        "tipo": "Triennale (L-18)",
        "descrizione": "Gestione di strutture ricettive, eventi, turismo d'impresa e marketing nel settore hospitality.",
        "materie_principali": ["Management Alberghiero", "Marketing del Turismo", "Revenue Management", "Diritto del Turismo", "Economia del Turismo"],
        "sbocchi_lavorativi": ["Direttore hotel", "Revenue manager", "Event planner", "Tourism product manager"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_turismo_manageriale": {
        "nome_completo": "Scienze del Turismo a Indirizzo Manageriale",
        "area": "Economia",
        "tipo": "Triennale (L-15)",
        "descrizione": "Competenze manageriali e culturali per operare nel settore turistico, con focus su destinazioni e strategie territoriali.",
        "materie_principali": ["Geografia del Turismo", "Economia del Turismo", "Gestione Destinazioni Turistiche", "Lingue", "Diritto del Turismo"],
        "sbocchi_lavorativi": ["Destination manager", "Consulente turismo sostenibile", "Tour operator", "Enti regionali promozione"],
        "durata": "3 anni (Triennale)"
    },
    "economia_aziendale_m": {
        "nome_completo": "Economia Aziendale (Magistrale)",
        "area": "Economia",
        "tipo": "Magistrale (LM-77)",
        "descrizione": "Approfondimento avanzato in strategia d'impresa, accounting internazionale, corporate governance e finanza.",
        "materie_principali": ["Corporate Finance", "Strategia Aziendale", "IFRS Accounting", "Business Analytics", "Governance e controllo"],
        "sbocchi_lavorativi": ["CFO", "Manager senior", "Revisore dei conti", "Consulente strategico"],
        "durata": "2 anni (Magistrale)"
    },
    "economia_commercio_m": {
        "nome_completo": "Economia e Commercio (Magistrale)",
        "area": "Economia",
        "tipo": "Magistrale (LM-56)",
        "descrizione": "Analisi economica avanzata, politiche pubbliche e internazionali, metodi quantitativi.",
        "materie_principali": ["Teoria Economica Avanzata", "Economia Pubblica", "Econometria Avanzata", "Economia dello Sviluppo"],
        "sbocchi_lavorativi": ["Economista senior", "Policy analyst", "Ricercatore universitario", "Banca d'Italia/Ue"],
        "durata": "2 anni (Magistrale)"
    },
    "finanza_m": {
        "nome_completo": "Finanza (Magistrale)",
        "area": "Economia",
        "tipo": "Magistrale (LM-16)",
        "descrizione": "Formazione specialistica in finanza quantitativa, mercati dei capitali, derivati e risk management.",
        "materie_principali": ["Finanza Quantitativa", "Derivati e Risk Management", "Asset Pricing", "Finanza Comportamentale", "Mercati dei Capitali"],
        "sbocchi_lavorativi": ["Analista quantitativo", "Portfolio manager", "Risk manager", "Investment banker"],
        "durata": "2 anni (Magistrale)"
    },

    # =========================================================
    # AREA 5 — FARMACIA
    # =========================================================
    "farmacia": {
        "nome_completo": "Farmacia",
        "area": "Farmacia",
        "tipo": "Magistrale a Ciclo Unico (LM-13) — Accesso programmato locale",
        "descrizione": "Formazione completa per la professione di farmacista: sintesi, analisi, distribuzione e counselling del farmaco.",
        "materie_principali": ["Chimica Farmaceutica", "Farmacologia", "Farmacognosia", "Tecnologia Farmaceutica", "Biochimica"],
        "sbocchi_lavorativi": ["Farmacista (territorio/ospedale)", "Industria farmaceutica", "Ricercatore", "Informatore scientifico"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "chimica_tecnologia_farmaceutiche": {
        "nome_completo": "Chimica e Tecnologia Farmaceutiche (CTF)",
        "area": "Farmacia",
        "tipo": "Magistrale a Ciclo Unico (LM-13) — Accesso programmato locale",
        "descrizione": "Laurea abilitante orientata alla sintesi chimica dei farmaci, al controllo analitico e alla ricerca in industria farmaceutica.",
        "materie_principali": ["Chimica Organica", "Chimica Farmaceutica Sintetica", "Analisi del Farmaco", "Biochimica", "Tecnologie Farmaceutiche"],
        "sbocchi_lavorativi": ["Chimico farmaceutico industriale", "Ricercatore farmaceutico", "Responsabile R&D", "Regulatory affairs"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "controllo_qualita": {
        "nome_completo": "Controllo di Qualità",
        "area": "Farmacia",
        "tipo": "Triennale (L-29)",
        "descrizione": "Formazione nelle tecniche analitiche per il controllo di qualità di farmaci, cosmetici, alimenti e prodotti sanitari.",
        "materie_principali": ["Chimica Analitica", "Analisi dei Farmaci", "Microbiologia", "Tossicologia", "Legislazione Farmaceutica"],
        "sbocchi_lavorativi": ["Analista di laboratorio", "Quality control specialist", "Tecnico industria cosmesi/farmaci"],
        "durata": "3 anni (Triennale)"
    },
    "scienze_tecnologie_erboristiche": {
        "nome_completo": "Scienze e Tecnologie Erboristiche",
        "area": "Farmacia",
        "tipo": "Triennale (L-29)",
        "descrizione": "Studio delle piante officinali, principi attivi naturali, preparazioni fitoterapiche e mercato erboristico.",
        "materie_principali": ["Botanica Farmaceutica", "Farmacognosia", "Fitoterapia", "Chimica dei Principi Attivi", "Legislazione"],
        "sbocchi_lavorativi": ["Erborista", "Consulente fitoterapeuta", "Operatore industria nutraceutica e cosmesi naturale"],
        "durata": "3 anni (Triennale)"
    },
    "scienze_nutraceutiche": {
        "nome_completo": "Scienze Nutraceutiche",
        "area": "Farmacia",
        "tipo": "Triennale (L-29)",
        "descrizione": "Formazione sugli alimenti funzionali e integratori alimentari, dall'analisi molecolare alla commercializzazione.",
        "materie_principali": ["Biochimica della Nutrizione", "Chimica degli Alimenti", "Farmacologia dei Nutraceutici", "Tecnologie dei Supplementi"],
        "sbocchi_lavorativi": ["Esperto nutraceutica", "R&D industria integratori", "Consulente salute e benessere"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 6 — GIURISPRUDENZA
    # =========================================================
    "giurisprudenza": {
        "nome_completo": "Giurisprudenza",
        "area": "Giurisprudenza",
        "tipo": "Magistrale a Ciclo Unico (LMG/01)",
        "descrizione": "Formazione giuridica completa in diritto civile, penale, costituzionale, amministrativo, commerciale e internazionale.",
        "materie_principali": ["Diritto Costituzionale", "Diritto Privato", "Diritto Penale", "Diritto Amministrativo", "Diritto Commerciale", "Diritto del Lavoro"],
        "sbocchi_lavorativi": ["Avvocato", "Magistrato", "Notaio", "Funzionario pubblico", "Giurista d'impresa"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "scienze_servizi_giuridici": {
        "nome_completo": "Scienze dei Servizi Giuridici",
        "area": "Giurisprudenza",
        "tipo": "Triennale (L-14)",
        "descrizione": "Percorso triennale orientato alle professioni giuridiche di supporto e alla pubblica amministrazione.",
        "materie_principali": ["Istituzioni di Diritto Privato", "Diritto Pubblico", "Diritto Penale", "Informatica Giuridica", "Diritto del Lavoro"],
        "sbocchi_lavorativi": ["Consulente legale d'ufficio", "Funzionario PA", "Mediatore civile", "Assistente in studi legali"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 7 — INGEGNERIA
    # =========================================================
    # --- TRIENNALI ---
    "ingegneria_informatica": {
        "nome_completo": "Ingegneria Informatica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-8)",
        "descrizione": "Progettazione di sistemi hardware e software, reti, sistemi operativi e architetture degli elaboratori.",
        "materie_principali": ["Programmazione", "Architettura degli Elaboratori", "Basi di Dati", "Reti di Calcolatori", "Ingegneria del Software"],
        "sbocchi_lavorativi": ["Sviluppatore Software", "Sistemista", "Progettista di Reti", "Analista"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "informatica": {
        "nome_completo": "Informatica (Scienze MM.FF.NN.)",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-31)",
        "descrizione": "Fondamenti teorici e applicativi dell'informatica: algoritmi, AI, crittografia e sicurezza informatica.",
        "materie_principali": ["Algoritmi", "Linguaggi di Programmazione", "Sistemi Operativi", "Basi di Dati", "Intelligenza Artificiale"],
        "sbocchi_lavorativi": ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", "Ricercatore IT"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_aerospaziale": {
        "nome_completo": "Ingegneria Aerospaziale",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Progettazione e gestione di velivoli, veicoli spaziali e sistemi aeronautici.",
        "materie_principali": ["Aerodinamica", "Meccanica del Volo", "Costruzioni Aeronautiche", "Propulsione", "Sistemi Spaziali"],
        "sbocchi_lavorativi": ["Ingegnere aerospaziale", "Industria aeronautica", "Enti spaziali (ASI/ESA)", "Aeronautica Militare"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "gestione_sistemi_aerospaziali_difesa": {
        "nome_completo": "Gestione dei Sistemi Aerospaziali per la Difesa",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Percorso orientato alla gestione di sistemi aeronautici e spaziali in ambito difesa e sicurezza nazionale.",
        "materie_principali": ["Sistemi Aeronautici Militari", "Logistica Aerospaziale", "Gestione Operazioni", "Diritto Internazionale Aereo"],
        "sbocchi_lavorativi": ["Ufficiale Aeronautica Militare", "Tecnico difesa", "Industria difesa aerospaziale"],
        "durata": "3 anni (Triennale)"
    },
    "ingegneria_biomedica": {
        "nome_completo": "Ingegneria Biomedica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Applicazione dell'ingegneria alla medicina: dispositivi medici, diagnostica per immagini e biomateriali.",
        "materie_principali": ["Fisiologia Umana", "Segnali Biomedici", "Dispositivi Medici", "Bioinstrumentazione", "Biomeccanica"],
        "sbocchi_lavorativi": ["Ingegnere biomedico", "Industria dispositivi medici", "Ospedali e cliniche", "Ricerca biomedica"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_chimica": {
        "nome_completo": "Ingegneria Chimica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Progettazione di processi chimici industriali, impianti petrolchimici, farmaceutici e per la sostenibilità ambientale.",
        "materie_principali": ["Chimica Fisica", "Operazioni Unitarie", "Termodinamica", "Reattori Chimici", "Impianti Chimici"],
        "sbocchi_lavorativi": ["Ingegnere di processo", "Industria chimica/petrolifera", "Energia e ambiente", "Ricercatore"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_civile": {
        "nome_completo": "Ingegneria Civile",
        "area": "Ingegneria",
        "tipo": "Triennale (L-7)",
        "descrizione": "Progettazione e costruzione di infrastrutture civili: strade, ponti, edifici e opere idrauliche.",
        "materie_principali": ["Scienza delle Costruzioni", "Geotecnica", "Idraulica", "Topografia", "Tecnica delle Costruzioni"],
        "sbocchi_lavorativi": ["Ingegnere civile", "Imprese edili", "Enti pubblici", "Libera professione"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_per_ambiente_territorio": {
        "nome_completo": "Ingegneria per l'Ambiente e il Territorio",
        "area": "Ingegneria",
        "tipo": "Triennale (L-7)",
        "descrizione": "Gestione delle risorse naturali, trattamento rifiuti, bonifica siti contaminati e rischio ambientale.",
        "materie_principali": ["Ecologia Applicata", "Trattamento delle Acque", "Gestione dei Rifiuti", "Rischio Idrogeologico"],
        "sbocchi_lavorativi": ["Ingegnere ambientale", "Consulente VIA/VAS", "Protezione Civile", "ARPA"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_gestionale_costruzioni": {
        "nome_completo": "Ingegneria Gestionale delle Costruzioni",
        "area": "Ingegneria",
        "tipo": "Triennale (L-7)",
        "descrizione": "Gestione tecnica ed economica di progetti e infrastrutture nel settore delle costruzioni.",
        "materie_principali": ["Project Management", "Economia dei Lavori Pubblici", "BIM", "Contrattualistica Pubblica"],
        "sbocchi_lavorativi": ["Project manager edile", "Construction manager", "Società di ingegneria", "Enti appaltanti"],
        "durata": "3 anni (Triennale)"
    },
    "ingegneria_automazione": {
        "nome_completo": "Ingegneria dell'Automazione",
        "area": "Ingegneria",
        "tipo": "Triennale (L-8)",
        "descrizione": "Sistemi di controllo automatico, robotica industriale, meccatronica e processi automatizzati.",
        "materie_principali": ["Controlli Automatici", "Robotica", "Elettronica", "Sistemi di Controllo Digitale", "Meccatronica"],
        "sbocchi_lavorativi": ["Ingegnere dell'automazione", "Sistemista di controllo", "Industria manifatturiera 4.0", "Robotica"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_telecomunicazioni_media": {
        "nome_completo": "Ingegneria delle Telecomunicazioni e dei Media Digitali",
        "area": "Ingegneria",
        "tipo": "Triennale (L-8)",
        "descrizione": "Reti di comunicazione, trasmissione dati, media digitali e tecnologie 5G/6G.",
        "materie_principali": ["Teoria dei Segnali", "Reti di Telecomunicazioni", "Antenne", "Sistemi di Trasmissione", "Media Digitali"],
        "sbocchi_lavorativi": ["Ingegnere TLC", "Network engineer", "R&D in telco", "Broadcasting digitale"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_elettrica": {
        "nome_completo": "Ingegneria Elettrica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Generazione, trasmissione e utilizzo dell'energia elettrica, macchine elettriche e smart grid.",
        "materie_principali": ["Circuiti Elettrici", "Macchine Elettriche", "Impianti Elettrici", "Elettrotecnica", "Sistemi Energetici"],
        "sbocchi_lavorativi": ["Ingegnere elettrico", "Progettista impianti", "Società energetiche", "Rinnovabili"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_elettronica": {
        "nome_completo": "Ingegneria Elettronica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-8)",
        "descrizione": "Progettazione di componenti e sistemi elettronici, microelettronica, sensori e sistemi embedded.",
        "materie_principali": ["Elettronica Analogica", "Elettronica Digitale", "Microcontrollori", "Sensori", "Progettazione VLSI"],
        "sbocchi_lavorativi": ["Ingegnere elettronico", "Embedded systems designer", "R&D microelettronica", "Automotive electronics"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_gestionale": {
        "nome_completo": "Ingegneria Gestionale",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Unisce competenze ingegneristiche con management aziendale, logistica, supply chain e analisi dei dati.",
        "materie_principali": ["Gestione della Produzione", "Logistica", "Economia e Organizzazione Aziendale", "Ricerca Operativa", "Operations Management"],
        "sbocchi_lavorativi": ["Operations manager", "Consulente management", "Supply chain manager", "Project manager"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_meccanica": {
        "nome_completo": "Ingegneria Meccanica",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Progettazione e realizzazione di macchine, sistemi meccanici, impianti industriali e produzione manifatturiera.",
        "materie_principali": ["Meccanica dei Solidi", "Macchine a Fluido", "Disegno Tecnico", "Tecnologia Meccanica", "Progettazione di Macchine"],
        "sbocchi_lavorativi": ["Ingegnere meccanico", "Progettista CAD/CAE", "Industria automotive e manifatturiera", "R&D"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_navale": {
        "nome_completo": "Ingegneria Navale",
        "area": "Ingegneria",
        "tipo": "Triennale (L-9)",
        "descrizione": "Progettazione di navi, imbarcazioni da diporto, impianti off-shore e sistemi di trasporto marittimo.",
        "materie_principali": ["Architettura Navale", "Propulsione Navale", "Strutture Navali", "Idrodinamica", "Impianti di Bordo"],
        "sbocchi_lavorativi": ["Ingegnere navale", "Progettista cantieristico", "Registro Navale", "Trasporto marittimo"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_edile": {
        "nome_completo": "Ingegneria Edile",
        "area": "Ingegneria",
        "tipo": "Triennale (L-23)",
        "descrizione": "Progettazione e gestione di edifici civili, con integrazione tra aspetti strutturali, impiantistici e architettonici.",
        "materie_principali": ["Tecnica delle Costruzioni", "Fisica Tecnica", "Topografia", "Impianti Tecnici", "Restauro Edilizio"],
        "sbocchi_lavorativi": ["Ingegnere edile", "Direttore lavori", "Collaudatore", "Libera professione"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ingegneria_edile_architettura": {
        "nome_completo": "Ingegneria Edile-Architettura (Ciclo Unico)",
        "area": "Ingegneria",
        "tipo": "Magistrale a Ciclo Unico (LM-4 C.U.)",
        "descrizione": "Percorso abilitante che unisce competenze strutturali ingegneristiche e progettuali architettoniche.",
        "materie_principali": ["Progettazione Architettonica", "Tecnica delle Costruzioni", "Impianti", "Urbanistica", "Restauro"],
        "sbocchi_lavorativi": ["Ingegnere-Architetto", "Progettista strutturale", "Libera professione"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "civil_environmental_engineering_eng": {
        "nome_completo": "Civil and Environmental Engineering (in inglese)",
        "area": "Ingegneria",
        "tipo": "Triennale (L-7) — In lingua inglese",
        "descrizione": "Corso internazionale in ingegneria civile e ambientale interamente erogato in lingua inglese.",
        "materie_principali": ["Structural Mechanics", "Geotechnics", "Hydraulics", "Environmental Engineering", "Calculus"],
        "sbocchi_lavorativi": ["Civil/Environmental Engineer (mercato internazionale)", "Multinazionali costruzioni"],
        "durata": "3 anni (Triennale)"
    },
    # --- MAGISTRALI INGEGNERIA ---
    "ingegneria_aerospaziale_m": {
        "nome_completo": "Ingegneria Aerospaziale (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-20)",
        "descrizione": "Progettazione avanzata di sistemi aeronautici e spaziali, aerodinamica computazionale e propulsione.",
        "materie_principali": ["Aerodinamica Avanzata", "Strutture Aerospaziali", "Propulsione Avanzata", "Sistemi Satellitari"],
        "sbocchi_lavorativi": ["Ingegnere aerospaziale senior", "ESA/NASA", "Industria difesa spaziale"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_biomedica_m": {
        "nome_completo": "Ingegneria Biomedica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-21)",
        "descrizione": "Progettazione avanzata di dispositivi medici, imagistica biomedica e ingegneria tissutale.",
        "materie_principali": ["Imaging Medicale", "Biomateriali", "Robotica Chirurgica", "Telemedicina"],
        "sbocchi_lavorativi": ["Ricercatore biomedico", "Industria medical device", "Ospedali tecnologici"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_chimica_m": {
        "nome_completo": "Ingegneria Chimica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-22)",
        "descrizione": "Ottimizzazione dei processi chimici, simulazione degli impianti e sviluppo di tecnologie verdi.",
        "materie_principali": ["Simulazione Processi", "Tecnologie Verdi", "Ingegneria delle Reazioni", "Processi di Separazione"],
        "sbocchi_lavorativi": ["Process engineer senior", "R&D chimica verde", "Industria petrolchimica"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_strutturale_geotecnica_m": {
        "nome_completo": "Ingegneria Strutturale e Geotecnica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-23)",
        "descrizione": "Progettazione avanzata di strutture e fondazioni, con attenzione all'ingegneria sismica.",
        "materie_principali": ["Dinamica Strutturale", "Ingegneria Sismica", "Geotecnica Avanzata", "Fondazioni Speciali"],
        "sbocchi_lavorativi": ["Strutturista senior", "Progettazione antisismica", "Grandi opere infrastrutturali"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_idraulica_trasporti_m": {
        "nome_completo": "Ingegneria dei Sistemi Idraulici e di Trasporto - ISIT (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-23)",
        "descrizione": "Gestione delle reti idriche, infrastrutture di trasporto e pianificazione della mobilità.",
        "materie_principali": ["Idraulica Urbana", "Infrastrutture Viarie", "Pianificazione dei Trasporti", "Idrologia"],
        "sbocchi_lavorativi": ["Ingegnere idraulico", "Progettista infrastrutture trasporto", "Autorità di bacino"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_edile_m": {
        "nome_completo": "Ingegneria Edile (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-24)",
        "descrizione": "Progettazione avanzata edile, efficienza energetica degli edifici, riqualificazione e facility management.",
        "materie_principali": ["Progettazione Edile Avanzata", "Efficienza Energetica", "BIM Avanzato", "Sistemi Impiantistici"],
        "sbocchi_lavorativi": ["Ingegnere edile senior", "Energy manager", "BIM manager"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_automazione_m": {
        "nome_completo": "Ingegneria dell'Automazione (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-25)",
        "descrizione": "Sistemi di controllo avanzati, robotica collaborativa, cyber-physical systems e intelligenza artificiale applicata.",
        "materie_principali": ["Controllo Robusto", "Robotica Avanzata", "Reti di Sensori", "Machine Learning per il Controllo"],
        "sbocchi_lavorativi": ["Automation engineer senior", "Industry 4.0 specialist", "R&D robotica"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_telecomunicazioni_m": {
        "nome_completo": "Ingegneria delle Telecomunicazioni (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-27)",
        "descrizione": "Reti wireless avanzate (5G/6G), comunicazioni satellitari, sicurezza delle reti e IoT.",
        "materie_principali": ["Reti Wireless Avanzate", "Propagazione delle Onde", "Cybersecurity", "IoT"],
        "sbocchi_lavorativi": ["Ingegnere TLC senior", "Progettista reti 5G", "Satellite engineer"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_elettrica_m": {
        "nome_completo": "Ingegneria Elettrica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-28)",
        "descrizione": "Reti elettriche intelligenti, azionamenti elettrici, compatibilità elettromagnetica e trasporti elettrici.",
        "materie_principali": ["Reti Elettriche Intelligenti", "Azionamenti Elettrici", "Compatibilità Elettromagnetica", "Veicoli Elettrici"],
        "sbocchi_lavorativi": ["Energy engineer", "Smart grid designer", "Automotive EV", "Terna/Enel R&D"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_elettronica_m": {
        "nome_completo": "Ingegneria Elettronica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-29)",
        "descrizione": "Microelettronica avanzata, progettazione di SoC, fotonica e sistemi embedded ad alte prestazioni.",
        "materie_principali": ["Progettazione SoC/VLSI", "Fotonica", "RF Electronics", "Advanced Embedded Systems"],
        "sbocchi_lavorativi": ["IC designer", "Embedded systems engineer", "R&D microelettronica/fotonica"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_gestionale_m": {
        "nome_completo": "Ingegneria Gestionale (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-31)",
        "descrizione": "Management industriale avanzato, digital supply chain, business analytics e circular economy.",
        "materie_principali": ["Operations Research Avanzata", "Digital Manufacturing", "Business Analytics", "Circular Economy"],
        "sbocchi_lavorativi": ["Operations manager senior", "Strategy consultant", "Data-driven manager"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_informatica_m": {
        "nome_completo": "Ingegneria Informatica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-32)",
        "descrizione": "Sistemi distribuiti, cloud computing, cybersecurity, intelligenza artificiale e big data engineering.",
        "materie_principali": ["Sistemi Distribuiti", "Cloud Computing", "Cybersecurity", "Intelligenza Artificiale", "Machine Learning"],
        "sbocchi_lavorativi": ["Software architect", "ML engineer", "Cloud architect", "Security engineer"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_meccanica_m": {
        "nome_completo": "Ingegneria Meccanica (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-33)",
        "descrizione": "Progettazione meccanica avanzata, additive manufacturing, tribologia e sistemi di propulsione.",
        "materie_principali": ["FEM Avanzato", "Additive Manufacturing", "Dinamica Avanzata dei Macchinari", "Tribologia"],
        "sbocchi_lavorativi": ["Design engineer senior", "R&D manifatturiero", "Automotive/aerospace industry"],
        "durata": "2 anni (Magistrale)"
    },
    "ingegneria_navale_m": {
        "nome_completo": "Ingegneria Navale (Magistrale)",
        "area": "Ingegneria",
        "tipo": "Magistrale (LM-34)",
        "descrizione": "Progettazione avanzata navale, propulsione ibrida/elettrica, sistemi off-shore e ingegneria del mare.",
        "materie_principali": ["Architettura Navale Avanzata", "Propulsione Ibrida/Elettrica", "Strutture Navali Avanzate", "Off-shore Engineering"],
        "sbocchi_lavorativi": ["Naval architect senior", "Off-shore engineer", "Fincantieri/cantieristica"],
        "durata": "2 anni (Magistrale)"
    },
    "informatica_m": {
        "nome_completo": "Informatica (Magistrale)",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Magistrale (LM-18)",
        "descrizione": "Approfondimento in informatica teorica, AI, sicurezza informatica e sistemi complessi.",
        "materie_principali": ["Teoria della Computazione", "Deep Learning", "Cybersecurity Avanzata", "Sistemi Multi-agente"],
        "sbocchi_lavorativi": ["Research scientist", "AI engineer", "Cybersecurity expert", "CTO startup"],
        "durata": "2 anni (Magistrale)"
    },

    # =========================================================
    # AREA 8 — MEDICINA E CHIRURGIA
    # =========================================================
    "medicina_chirurgia": {
        "nome_completo": "Medicina e Chirurgia",
        "area": "Medicina e Chirurgia",
        "tipo": "Magistrale a Ciclo Unico (LM-41) — Accesso programmato nazionale",
        "descrizione": "Formazione medica completa per il conseguimento dell'abilitazione alla professione di medico chirurgo.",
        "materie_principali": ["Anatomia", "Fisiologia", "Patologia Generale", "Farmacologia", "Clinica Medica e Chirurgica"],
        "sbocchi_lavorativi": ["Medico Chirurgo", "Specialista SSN", "Ricercatore clinico", "Medico di base"],
        "durata": "6 anni (Ciclo Unico)"
    },
    "medicina_chirurgia_inglese": {
        "nome_completo": "Medicina e Chirurgia (in lingua inglese)",
        "area": "Medicina e Chirurgia",
        "tipo": "Magistrale a Ciclo Unico (LM-41) — In lingua inglese — Accesso programmato nazionale",
        "descrizione": "Percorso identico a Medicina e Chirurgia, interamente erogato in lingua inglese per studenti italiani e internazionali.",
        "materie_principali": ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Clinical Medicine"],
        "sbocchi_lavorativi": ["Medical Doctor (mercato internazionale)", "Specialista clinico", "Ricercatore"],
        "durata": "6 anni (Ciclo Unico)"
    },
    "medicina_chirurgia_tecnologico": {
        "nome_completo": "Medicina e Chirurgia ad Indirizzo Tecnologico",
        "area": "Medicina e Chirurgia",
        "tipo": "Magistrale a Ciclo Unico (LM-41)",
        "descrizione": "Percorso innovativo che integra la formazione medica classica con tecnologie digitali, AI e robotica chirurgica.",
        "materie_principali": ["Anatomia", "Clinica Medica", "Robotica Chirurgica", "AI in Medicina", "Digital Health"],
        "sbocchi_lavorativi": ["Medico tecnologo", "Chirurgo robotico", "Specialista digital health"],
        "durata": "6 anni (Ciclo Unico)"
    },
    "odontoiatria_protesi_dentaria": {
        "nome_completo": "Odontoiatria e Protesi Dentaria",
        "area": "Medicina e Chirurgia",
        "tipo": "Magistrale a Ciclo Unico (LM-46) — Accesso programmato nazionale",
        "descrizione": "Formazione completa per la professione di odontoiatra: diagnosi, prevenzione e trattamento delle patologie orali.",
        "materie_principali": ["Anatomia Dentale", "Odontoiatria Conservativa", "Protesi Dentaria", "Ortognatodonzia", "Chirurgia Orale"],
        "sbocchi_lavorativi": ["Odontoiatra", "Ortodontista (dopo specializzazione)", "Libera professione"],
        "durata": "6 anni (Ciclo Unico)"
    },
    # --- Professioni Sanitarie (Triennali) ---
    "infermieristica": {
        "nome_completo": "Infermieristica",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT1) — Accesso programmato nazionale",
        "descrizione": "Formazione dell'infermiere professionale per la cura e l'assistenza del paziente in ambito ospedaliero e territoriale.",
        "materie_principali": ["Scienze Infermieristiche", "Anatomia e Fisiologia", "Farmacologia", "Tirocinio Clinico"],
        "sbocchi_lavorativi": ["Infermiere (SSN)", "Case manager", "Infermiere domiciliare"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "infermieristica_pediatrica": {
        "nome_completo": "Infermieristica Pediatrica",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT1) — Accesso programmato nazionale",
        "descrizione": "Formazione specializzata nell'assistenza infermieristica al bambino e all'adolescente.",
        "materie_principali": ["Pediatria Clinica", "Neonatologia", "Infermieristica Pediatrica", "Tirocinio Pediatrico"],
        "sbocchi_lavorativi": ["Infermiere pediatrico (SSN)", "Neonatologia", "Pediatria ospedaliera"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "ostetricia": {
        "nome_completo": "Ostetricia",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT1) — Accesso programmato nazionale",
        "descrizione": "Formazione dell'ostetrica/o per l'assistenza alla gravidanza, al parto e al puerperio.",
        "materie_principali": ["Ostetricia Clinica", "Ginecologia", "Anatomia Funzionale", "Tirocinio Ostetrico"],
        "sbocchi_lavorativi": ["Ostetrica/o (SSN)", "Consultori familiari", "Libera professione"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "fisioterapia": {
        "nome_completo": "Fisioterapia",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT2) — Accesso programmato nazionale",
        "descrizione": "Riabilitazione funzionale di pazienti con patologie ortopediche, neurologiche e cardiorespiratorias.",
        "materie_principali": ["Biomeccanica", "Chinesiologia", "Neurologia Riabilitativa", "Fisioterapia Muscolo-Scheletrica"],
        "sbocchi_lavorativi": ["Fisioterapista (SSN/privato)", "Riabilitazione sportiva", "Libera professione"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "logopedia": {
        "nome_completo": "Logopedia",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT2) — Accesso programmato nazionale",
        "descrizione": "Prevenzione, diagnosi e trattamento dei disturbi della comunicazione, della voce e della deglutizione.",
        "materie_principali": ["Foniatria", "Neuropsicologia del Linguaggio", "Terapia dei DSA", "Disfagia"],
        "sbocchi_lavorativi": ["Logopedista (SSN/privato)", "Scuole", "Riabilitazione neurologica"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "ortottica_oftalmologia": {
        "nome_completo": "Ortottica ed Assistenza Oftalmologica",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT2) — Accesso programmato nazionale",
        "descrizione": "Diagnosi e trattamento dei disturbi della motilità oculare e delle funzioni visive.",
        "materie_principali": ["Anatomia dell'Occhio", "Ortottica", "Strumentazione Oftalmica", "Tirocinio Clinico"],
        "sbocchi_lavorativi": ["Ortottista (SSN/privato)", "Centri di oculistica", "Optometria clinica"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "dietistica": {
        "nome_completo": "Dietistica",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Formazione del dietista per la pianificazione di regimi alimentari terapeutici e preventivi.",
        "materie_principali": ["Biochimica della Nutrizione", "Dietetica Clinica", "Patologie Metaboliche", "Ristorazione Collettiva"],
        "sbocchi_lavorativi": ["Dietista (SSN/privato)", "Ristorazione ospedaliera", "Consulente nutrizionale"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "igiene_dentale": {
        "nome_completo": "Igiene Dentale",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Prevenzione e trattamento delle patologie del cavo orale in supporto all'odontoiatra.",
        "materie_principali": ["Anatomia Dentale", "Parodontologia", "Tecniche di Igiene Orale", "Radiologia Dentale"],
        "sbocchi_lavorativi": ["Igienista dentale (studi odontoiatrici/SSN)"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_laboratorio_biomedico": {
        "nome_completo": "Tecniche di Laboratorio Biomedico",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Esecuzione ed interpretazione di analisi di laboratorio clinico, microbiologico, immunologico e molecolare.",
        "materie_principali": ["Chimica Clinica", "Ematologia", "Microbiologia Clinica", "Biologia Molecolare Diagnostica"],
        "sbocchi_lavorativi": ["TSLB (SSN/laboratori privati)", "Controllo qualità diagnostica"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_radiologia_medica": {
        "nome_completo": "Tecniche di Radiologia Medica per Immagini e Radioterapia",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Esecuzione di esami diagnostici per immagini (RX, TC, RMN) e trattamenti radioterapici.",
        "materie_principali": ["Radiologia Diagnostica", "TC e RMN", "Radioterapia", "Fisica Medica"],
        "sbocchi_lavorativi": ["TSRM (SSN/privato)", "Radiologia diagnostica", "Radioterapia oncologica"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_neurofisiopatologia": {
        "nome_completo": "Tecniche di Neurofisiopatologia",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Esecuzione di indagini neurofisiologiche cliniche (EEG, EMG, potenziali evocati) per la diagnosi neurologica.",
        "materie_principali": ["Neurofisiologia Clinica", "Elettroencefalografia", "Elettromiografia", "Neurologia"],
        "sbocchi_lavorativi": ["Tecnico di neurofisiopatologia (SSN/centri neurologici)"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_audiometriche": {
        "nome_completo": "Tecniche Audiometriche",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Diagnosi e riabilitazione dei disturbi dell'udito attraverso tecniche audiometriche avanzate.",
        "materie_principali": ["Audiologia", "Audiometria Clinica", "Audiometria Infantile", "Riabilitazione Uditiva"],
        "sbocchi_lavorativi": ["Tecnico audiologo (SSN/centri audiologici)"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_audioprotesiche": {
        "nome_completo": "Tecniche Audioprotesiche",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Selezione, adattamento e manutenzione delle protesi acustiche e degli impianti cocleari.",
        "materie_principali": ["Audiologia Protesica", "Elettroacustica", "Riabilitazione Uditiva", "Tirocinio Professionale"],
        "sbocchi_lavorativi": ["Audioprotesista (centri acustici/SSN)"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_fisiopatologia_cardiocircolatoria": {
        "nome_completo": "Tecniche di Fisiopatologia Cardiocircolatoria e Perfusione Cardiovascolare",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT3) — Accesso programmato nazionale",
        "descrizione": "Gestione della circolazione extracorporea durante la cardiochirurgia e monitoraggio cardiologico avanzato.",
        "materie_principali": ["Cardiologia Clinica", "Circolazione Extracorporea", "ECG Avanzato", "Ecocardiografia"],
        "sbocchi_lavorativi": ["Perfusionista cardiovascolare (sale operatorie di cardiochirurgia)"],
        "durata": "3 anni (Triennale abilitante)"
    },
    "tecniche_prevenzione_ambiente_lavoro": {
        "nome_completo": "Tecniche della Prevenzione nell'Ambiente e nei Luoghi di Lavoro",
        "area": "Medicina e Chirurgia",
        "tipo": "Triennale (L/SNT4) — Accesso programmato nazionale",
        "descrizione": "Vigilanza igienico-sanitaria, sicurezza sul lavoro, prevenzione collettiva e controllo alimenti.",
        "materie_principali": ["Igiene Ambientale", "Medicina del Lavoro", "Sicurezza e HACCP", "Epidemiologia"],
        "sbocchi_lavorativi": ["TPALL (ASL/ARPA)", "Responsabile sicurezza aziendale (RSPP)", "Ispettore sanitario"],
        "durata": "3 anni (Triennale abilitante)"
    },

    # =========================================================
    # AREA 9 — MEDICINA VETERINARIA
    # =========================================================
    "medicina_veterinaria": {
        "nome_completo": "Medicina Veterinaria",
        "area": "Medicina Veterinaria",
        "tipo": "Magistrale a Ciclo Unico (LM-42) — Accesso programmato nazionale",
        "descrizione": "Formazione completa per la professione veterinaria: diagnosi, terapia, chirurgia veterinaria e sanità pubblica animale.",
        "materie_principali": ["Anatomia Veterinaria", "Patologia Animale", "Chirurgia Veterinaria", "Farmacologia Veterinaria", "Sanità Pubblica"],
        "sbocchi_lavorativi": ["Medico Veterinario", "Sanità pubblica veterinaria (ASL)", "Industria zootecnica", "Ricercatore"],
        "durata": "5 anni (Ciclo Unico)"
    },
    "gestione_animali_produzioni": {
        "nome_completo": "Gestione degli Animali e delle Produzioni",
        "area": "Medicina Veterinaria",
        "tipo": "Triennale (L-38)",
        "descrizione": "Gestione degli allevamenti, zootecnia, benessere animale e valorizzazione delle produzioni zootecniche.",
        "materie_principali": ["Zootecnia Generale", "Benessere Animale", "Nutrizione Animale", "Genetica degli Allevamenti"],
        "sbocchi_lavorativi": ["Zootecnico", "Consulente allevamenti", "Industria mangimistica", "Agenzie di controllo"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 10 — SCIENZE MM.FF.NN.
    # =========================================================
    "biologia": {
        "nome_completo": "Biologia",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-13) — Accesso programmato locale",
        "descrizione": "Studio degli organismi viventi a livello molecolare, cellulare, sistemico ed ecologico.",
        "materie_principali": ["Biologia Molecolare", "Biologia Cellulare", "Genetica", "Ecologia", "Fisiologia"],
        "sbocchi_lavorativi": ["Biologo", "Ricercatore", "Tecnico di laboratorio", "Insegnante (con abilitazione)"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "biology_one_health": {
        "nome_completo": "Biology for One-health (in inglese)",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-13) — In lingua inglese — Accesso programmato locale",
        "descrizione": "Biologia orientata all'approccio One Health: interconnessione tra salute umana, animale e ambientale.",
        "materie_principali": ["Ecology", "Epidemiology", "Microbiology", "Conservation Biology", "Environmental Health"],
        "sbocchi_lavorativi": ["Environmental biologist", "Public health researcher", "Conservation scientist"],
        "durata": "3 anni (Triennale)"
    },
    "chimica": {
        "nome_completo": "Chimica",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-27)",
        "descrizione": "Fondamenti della chimica pura: organica, inorganica, analitica e fisico-chimica.",
        "materie_principali": ["Chimica Organica", "Chimica Inorganica", "Chimica Analitica", "Chimica Fisica", "Laboratori Sperimentali"],
        "sbocchi_lavorativi": ["Chimico", "Ricercatore", "Controllo qualità", "Industria chimica"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "chimica_industriale": {
        "nome_completo": "Chimica Industriale",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-27)",
        "descrizione": "Applicazione della chimica ai processi industriali: sintesi, polimeri, materiali e energia.",
        "materie_principali": ["Chimica dei Polimeri", "Catalisi Industriale", "Chimica dei Materiali", "Processi Chimici Industriali"],
        "sbocchi_lavorativi": ["Chimico industriale", "R&D materiali", "Industria polimerica e petrolchimica"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "fisica": {
        "nome_completo": "Fisica",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-30)",
        "descrizione": "Studio delle leggi fondamentali della natura, dalla meccanica classica alla fisica quantistica e all'astrofisica.",
        "materie_principali": ["Meccanica Classica", "Elettromagnetismo", "Meccanica Quantistica", "Laboratori Sperimentali", "Fisica Moderna"],
        "sbocchi_lavorativi": ["Fisico (INFN/CNR)", "Ricercatore", "Insegnante", "Data scientist", "Finanza quantitativa"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "matematica": {
        "nome_completo": "Matematica",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-35)",
        "descrizione": "Algebra, analisi matematica, geometria, probabilità e fondamenti della matematica pura e applicata.",
        "materie_principali": ["Analisi Matematica", "Geometria", "Algebra", "Probabilità e Statistica", "Analisi Numerica"],
        "sbocchi_lavorativi": ["Matematico", "Ricercatore", "Attuario", "Data analyst", "Insegnante"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "ottica_optometria": {
        "nome_completo": "Ottica e Optometria",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-30)",
        "descrizione": "Studio della luce e delle sue applicazioni, correzione dei difetti visivi e strumentazione ottica.",
        "materie_principali": ["Ottica Fisica", "Optometria", "Strumentazione Ottica", "Lenti a Contatto", "Elettro-ottica"],
        "sbocchi_lavorativi": ["Ottico optometrista", "R&D fotonica", "Industria ottica e laser"],
        "durata": "3 anni (Triennale)"
    },
    "scienze_geologiche": {
        "nome_completo": "Scienze Geologiche",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-34)",
        "descrizione": "Evoluzione del pianeta, mineralogia, petrografia, geofisica e rischi naturali.",
        "materie_principali": ["Geologia", "Mineralogia", "Petrografia", "Geofisica", "Paleontologia"],
        "sbocchi_lavorativi": ["Geologo", "Tecnico del territorio", "Protezione Civile", "Ricercatore"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_natura_ambiente": {
        "nome_completo": "Scienze per la Natura e per l'Ambiente",
        "area": "Scienze MM.FF.NN.",
        "tipo": "Triennale (L-32)",
        "descrizione": "Ecologia, biologia della conservazione, scienze ambientali e gestione degli ecosistemi naturali.",
        "materie_principali": ["Ecologia", "Botanica", "Zoologia", "Chimica Ambientale", "Gestione delle Risorse Naturali"],
        "sbocchi_lavorativi": ["Ecologo", "Naturalista", "Consulente ambientale", "Tecnico parchi naturali"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 11 — SCIENZE POLITICHE
    # =========================================================
    "scienze_politiche": {
        "nome_completo": "Scienze Politiche",
        "area": "Scienze Politiche",
        "tipo": "Triennale (L-36)",
        "descrizione": "Analisi politica, istituzioni, relazioni internazionali, diritto pubblico ed economia politica.",
        "materie_principali": ["Scienza della Politica", "Storia Contemporanea", "Diritto Pubblico", "Economia Politica", "Relazioni Internazionali"],
        "sbocchi_lavorativi": ["Diplomatico", "Funzionario pubblico", "ONG/organizzazioni internazionali", "Giornalismo politico"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_amministrazione_organizzazione": {
        "nome_completo": "Scienze dell'Amministrazione e dell'Organizzazione",
        "area": "Scienze Politiche",
        "tipo": "Triennale (L-16)",
        "descrizione": "Gestione dei sistemi amministrativi pubblici e privati, organizzazione aziendale e policy making.",
        "materie_principali": ["Diritto Amministrativo", "Sociologia delle Organizzazioni", "Economia Pubblica", "Informatica Giuridica"],
        "sbocchi_lavorativi": ["Funzionario PA", "HR manager", "Consulente organizzativo", "Esperto di policy"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "servizio_sociale": {
        "nome_completo": "Servizio Sociale",
        "area": "Scienze Politiche",
        "tipo": "Triennale (L-39)",
        "descrizione": "Formazione dell'assistente sociale per interventi a sostegno di individui, famiglie e comunità vulnerabili.",
        "materie_principali": ["Servizio Sociale", "Sociologia", "Psicologia Clinica", "Diritto di Famiglia", "Politiche Sociali"],
        "sbocchi_lavorativi": ["Assistente sociale (ASL/Comuni)", "Operatore sociale", "Terzo settore"],
        "durata": "3 anni (Triennale)"
    },
    "statistica_impresa_societa": {
        "nome_completo": "Statistica per l'Impresa e la Società",
        "area": "Scienze Politiche",
        "tipo": "Triennale (L-41)",
        "descrizione": "Metodi statistici e quantitativi per l'analisi economica, sociale e di mercato.",
        "materie_principali": ["Statistica", "Probabilità", "Econometria", "Analisi dei Dati", "Matematica Finanziaria"],
        "sbocchi_lavorativi": ["Statistico", "Data analyst", "Attuario", "Ricercatore di mercato", "Business intelligence"],
        "durata": "3 anni (Triennale)"
    },

    # =========================================================
    # AREA 12 — SCIENZE SOCIALI
    # =========================================================
    "culture_digitali_comunicazione": {
        "nome_completo": "Culture Digitali e della Comunicazione",
        "area": "Scienze Sociali",
        "tipo": "Triennale (L-40)",
        "descrizione": "Analisi dei media digitali, comunicazione online, sociologia dei media e cultural studies.",
        "materie_principali": ["Sociologia dei Media", "Digital Communication", "Semiotica", "Cultura Digitale", "Media Studies"],
        "sbocchi_lavorativi": ["Social media manager", "Content strategist", "Ricercatore culturale", "Comunicazione istituzionale"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "sociologia": {
        "nome_completo": "Sociologia",
        "area": "Scienze Sociali",
        "tipo": "Triennale (L-40)",
        "descrizione": "Studio delle dinamiche sociali, delle organizzazioni, dei processi di cambiamento e delle disuguaglianze.",
        "materie_principali": ["Sociologia Generale", "Ricerca Sociale", "Sociologia Urbana", "Psicologia Sociale", "Statistica Sociale"],
        "sbocchi_lavorativi": ["Sociologo", "Ricercatore sociale", "HR", "Terzo settore", "ONG"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },

    # =========================================================
    # AREA 13 — STUDI UMANISTICI
    # =========================================================
    "archeologia_storia_arti_patrimonio": {
        "nome_completo": "Archeologia, Storia delle Arti e Scienze del Patrimonio Culturale",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-1)",
        "descrizione": "Studio del patrimonio culturale materiale e immateriale, dalla preistoria all'età contemporanea, con scavi e analisi dei beni culturali.",
        "materie_principali": ["Archeologia", "Storia dell'Arte", "Museologia", "Conservazione dei Beni Culturali", "Numismatica"],
        "sbocchi_lavorativi": ["Archeologo", "Storico dell'arte", "Curatore museale", "Funzionario MiC", "Operatore beni culturali"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "filosofia": {
        "nome_completo": "Filosofia",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-5)",
        "descrizione": "Pensiero filosofico dalla filosofia antica alla contemporanea, etica, logica e filosofia della mente.",
        "materie_principali": ["Filosofia Teoretica", "Storia della Filosofia", "Logica", "Etica", "Filosofia del Linguaggio"],
        "sbocchi_lavorativi": ["Insegnante Filosofia", "Editoria", "Consulente etico", "Ricercatore", "HR"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "lettere_classiche": {
        "nome_completo": "Lettere Classiche",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-10)",
        "descrizione": "Letteratura, lingua e cultura greca e latina, filologia classica, storia antica e papirologia.",
        "materie_principali": ["Latino", "Greco Antico", "Letteratura Latina e Greca", "Storia Romana", "Papirologia"],
        "sbocchi_lavorativi": ["Insegnante Lettere Classiche", "Filologo", "Ricercatore accademico", "Operatore culturale"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "lettere_moderne": {
        "nome_completo": "Lettere Moderne",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-10)",
        "descrizione": "Letteratura italiana e comparata, linguistica, storia moderna, critica letteraria e culturale.",
        "materie_principali": ["Letteratura Italiana", "Linguistica Italiana", "Storia Moderna", "Letteratura Comparata", "Filologia Romanza"],
        "sbocchi_lavorativi": ["Insegnante Lettere", "Giornalista", "Editoria", "Operatore culturale", "Scrittura creativa"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "lingue_culture_letterature_moderne": {
        "nome_completo": "Lingue, Culture e Letterature Moderne Europee",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-11)",
        "descrizione": "Studio di due lingue e letterature europee moderne in prospettiva comparativa e interculturale.",
        "materie_principali": ["Lingua e Letteratura (2 lingue europee)", "Linguistica Generale", "Storia Europea", "Traduzione"],
        "sbocchi_lavorativi": ["Traduttore/Interprete", "Operatore culturale internazionale", "Insegnante lingue", "Enti europei"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "scienze_tecniche_psicologiche": {
        "nome_completo": "Scienze e Tecniche Psicologiche",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-24)",
        "descrizione": "Processi cognitivi, emotivi e comportamentali dell'individuo. Base per l'accesso alla magistrale in psicologia.",
        "materie_principali": ["Psicologia Generale", "Psicometria", "Psicobiologia", "Psicologia dello Sviluppo", "Psicologia Sociale"],
        "sbocchi_lavorativi": ["Operatore psicosociale", "HR junior", "Ricerca psicologica", "Accesso a LM-51 (Psicologia Clinica)"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
    "storia": {
        "nome_completo": "Storia",
        "area": "Studi Umanistici",
        "tipo": "Triennale (L-42)",
        "descrizione": "Dalla storia antica alla contemporanea, archivistica, metodologia storica e storia del Mediterraneo.",
        "materie_principali": ["Storia Medievale", "Storia Moderna", "Storia Contemporanea", "Archivistica", "Metodologia Storica"],
        "sbocchi_lavorativi": ["Insegnante Storia", "Archivista", "Storico ricercatore", "Operatore culturale", "Giornalismo storico"],
        "durata": "3 anni (Triennale) + 2 anni (Magistrale)"
    },
}

# =========================================================
# METADATI ATENEO (utili all'agente per risposte contestuali)
# =========================================================
METADATI_ATENEO = {
    "nome": "Università degli Studi di Napoli Federico II",
    "acronimo": "UniNa",
    "sito_ufficiale": "https://www.unina.it",
    "anno_fondazione": 1224,
    "fondatore": "Imperatore Federico II di Svevia",
    "numero_dipartimenti": 26,
    "numero_corsi_totale": "172+",
    "numero_studenti": "80.000+",
    "aree_didattiche": [
        "Agraria",
        "Architettura",
        "Biotecnologie della Salute",
        "Economia",
        "Farmacia",
        "Giurisprudenza",
        "Ingegneria",
        "Medicina e Chirurgia",
        "Medicina Veterinaria",
        "Scienze MM.FF.NN.",
        "Scienze Politiche",
        "Scienze Sociali",
        "Studi Umanistici",
    ],
    "portale_iscrizioni": "https://www.segrepass.unina.it",
    "note": (
        "La Federico II è una delle università più antiche del mondo, "
        "fondata con atto imperiale nel 1224. Offre 78 triennali, 84 magistrali "
        "e 10 magistrali a ciclo unico. La maggior parte dei corsi è ad accesso libero; "
        "quelli a numero programmato richiedono TOLC o test specifici (es. Medicina, Architettura, Farmacia, "
        "Biotecnologie, corsi delle Professioni Sanitarie). "
        "La no-tax area è fissata a 30.000 € ISEE."
    )
}