-- ============================================================================
-- LearnAI Platform — Dati Seed
-- Dati iniziali per tutti i moduli. Ogni gruppo può aggiungere i propri.
-- ============================================================================

-- === COMPETENZE (catalogo condiviso) ===
INSERT OR IGNORE INTO skills (id, nome, categoria, descrizione) VALUES
(1,  'Python',              'Technical', 'Linguaggio di programmazione Python'),
(2,  'SQL',                 'Technical', 'Structured Query Language per database'),
(3,  'Excel Avanzato',      'Technical', 'Funzioni avanzate, pivot, macro'),
(4,  'Power BI',            'Technical', 'Strumento di Business Intelligence Microsoft'),
(5,  'Statistica',          'Technical', 'Statistica descrittiva e inferenziale'),
(6,  'Machine Learning',    'Technical', 'Algoritmi di apprendimento automatico'),
(7,  'Data Visualization',  'Technical', 'Creazione di grafici e dashboard efficaci'),
(8,  'AI / GenAI',          'Technical', 'Intelligenza artificiale generativa e prompt engineering'),
(9,  'Cloud Computing',     'Technical', 'Servizi cloud (AWS, Azure, GCP)'),
(10, 'Prompt Engineering',  'Technical', 'Tecniche per interagire efficacemente con LLM'),
(11, 'Project Management',  'Soft',      'Gestione di progetti e timeline'),
(12, 'Comunicazione',       'Soft',      'Comunicazione efficace scritta e orale'),
(13, 'Problem Solving',     'Soft',      'Analisi e risoluzione di problemi complessi'),
(14, 'Leadership',          'Soft',      'Guida e motivazione del team'),
(15, 'Teamwork',            'Soft',      'Collaborazione e lavoro di squadra'),
(16, 'Pensiero Critico',    'Soft',      'Valutazione oggettiva di informazioni'),
(17, 'Digital Marketing',   'Domain',    'Marketing digitale e strategie online'),
(18, 'Finance',             'Domain',    'Concetti finanziari e analisi di bilancio'),
(19, 'HR Management',       'Domain',    'Gestione risorse umane'),
(20, 'Operations',          'Domain',    'Gestione dei processi operativi aziendali');

-- === UTENTI DI ESEMPIO ===
INSERT OR IGNORE INTO users (id, nome, cognome, email, ruolo, dipartimento, data_assunzione) VALUES
(1, 'Marco',      'Bianchi',   'marco.bianchi@learnai.it',    'Junior Data Analyst',       'IT',         '2025-01-15'),
(2, 'Giulia',     'Verdi',     'giulia.verdi@learnai.it',     'Marketing Specialist',      'Marketing',  '2025-02-01'),
(3, 'Alessandro', 'Rossi',     'alessandro.rossi@learnai.it', 'Project Manager',           'Operations', '2024-11-01'),
(4, 'Luca',       'Ferrari',   'luca.ferrari@learnai.it',     'HR Coordinator',            'HR',         '2025-01-20'),
(5, 'Sara',       'Romano',    'sara.romano@learnai.it',      'Business Analyst',          'Finance',    '2024-12-01');

-- === COMPETENZE UTENTI (livelli attuali e target) ===
-- Marco Bianchi (Junior Data Analyst)
INSERT OR IGNORE INTO user_skills (user_id, skill_id, livello_attuale, livello_target) VALUES
(1, 1, 2, 4),   -- Python: 2/5 → target 4
(1, 2, 2, 4),   -- SQL: 2/5 → target 4
(1, 3, 4, 4),   -- Excel: 4/5 → target 4
(1, 5, 3, 4),   -- Statistica: 3/5 → target 4
(1, 6, 1, 3),   -- ML: 1/5 → target 3
(1, 7, 2, 4),   -- Data Viz: 2/5 → target 4
(1, 13, 3, 4);  -- Problem Solving: 3/5 → target 4

-- Giulia Verdi (Marketing Specialist)
INSERT OR IGNORE INTO user_skills (user_id, skill_id, livello_attuale, livello_target) VALUES
(2, 3, 3, 4),   -- Excel: 3/5
(2, 7, 3, 4),   -- Data Viz: 3/5
(2, 8, 1, 3),   -- AI/GenAI: 1/5
(2, 12, 4, 5),  -- Comunicazione: 4/5
(2, 17, 4, 5);  -- Digital Marketing: 4/5

-- Alessandro Rossi (Project Manager)
INSERT OR IGNORE INTO user_skills (user_id, skill_id, livello_attuale, livello_target) VALUES
(3, 2, 2, 3),   -- SQL: 2/5
(3, 3, 3, 4),   -- Excel: 3/5
(3, 11, 4, 5),  -- Project Management: 4/5
(3, 12, 4, 5),  -- Comunicazione: 4/5
(3, 14, 3, 5),  -- Leadership: 3/5
(3, 13, 4, 5);  -- Problem Solving: 4/5

-- === CATALOGO CORSI ===
INSERT OR IGNORE INTO courses (id, titolo, descrizione, categoria, durata_ore, livello, prerequisiti_json) VALUES
(1,  'Fondamenti di Python',
     'Introduzione alla programmazione con Python: variabili, funzioni, strutture dati, librerie base.',
     'Data Science', 20, 'base', '[]'),

(2,  'SQL per Business',
     'Query SQL per estrarre e analizzare dati aziendali: SELECT, JOIN, GROUP BY, subquery.',
     'Data Science', 15, 'base', '[]'),

(3,  'Excel Avanzato e Power Query',
     'Funzioni avanzate, tabelle pivot, Power Query, automazione con macro VBA.',
     'Business Tools', 12, 'intermedio', '[]'),

(4,  'Statistica per Data Analysis',
     'Statistica descrittiva, distribuzioni, test di ipotesi, correlazione e regressione.',
     'Data Science', 18, 'intermedio', '[]'),

(5,  'Data Visualization con Python',
     'Matplotlib, Seaborn, Plotly: creare grafici efficaci e dashboard interattive.',
     'Data Science', 15, 'intermedio', '[1]'),

(6,  'Introduzione al Machine Learning',
     'Concetti base di ML: classificazione, regressione, clustering. Scikit-learn.',
     'Data Science', 25, 'intermedio', '[1, 4]'),

(7,  'Power BI Fundamentals',
     'Creare report e dashboard interattive con Power BI Desktop e Power BI Service.',
     'Business Tools', 15, 'base', '[]'),

(8,  'AI e Prompt Engineering',
     'Comprendere l''AI generativa, scrivere prompt efficaci, integrare LLM nel lavoro.',
     'AI', 10, 'base', '[]'),

(9,  'Project Management Agile',
     'Scrum, Kanban, gestione sprint, retrospettive, strumenti di PM.',
     'Management', 15, 'intermedio', '[]'),

(10, 'Digital Marketing Analytics',
     'Google Analytics, A/B testing, funnel analysis, attribution modeling.',
     'Marketing', 12, 'intermedio', '[]'),

(11, 'Python per Data Science',
     'Pandas, NumPy, analisi dati avanzata, pulizia dataset, feature engineering.',
     'Data Science', 20, 'intermedio', '[1]'),

(12, 'Machine Learning Avanzato',
     'Deep learning, NLP, time series, deployment di modelli ML.',
     'Data Science', 30, 'avanzato', '[6]'),

(13, 'Cloud Computing Essentials',
     'Fondamenti di AWS: S3, EC2, Lambda, IAM. Architetture cloud.',
     'Cloud', 15, 'base', '[]'),

(14, 'Leadership e Gestione del Team',
     'Stili di leadership, delega, feedback, gestione conflitti, motivazione.',
     'Management', 12, 'intermedio', '[]'),

(15, 'Comunicazione Efficace',
     'Public speaking, storytelling con i dati, presentazioni d''impatto.',
     'Soft Skills', 10, 'base', '[]');
