DROP TABLE IF EXISTS prediction_logs;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id_employee INTEGER PRIMARY KEY,
    age INTEGER NOT NULL,
    genre VARCHAR(10) NOT NULL,
    revenu_mensuel DOUBLE PRECISION NOT NULL,
    statut_marital VARCHAR(50) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    poste VARCHAR(100) NOT NULL,
    nombre_experiences_precedentes INTEGER NOT NULL,
    nombre_heures_travailless INTEGER,
    annee_experience_totale INTEGER NOT NULL,
    annees_dans_l_entreprise INTEGER NOT NULL,
    annees_dans_le_poste_actuel INTEGER NOT NULL,
    satisfaction_employee_environnement INTEGER NOT NULL,
    note_evaluation_precedente INTEGER NOT NULL,
    niveau_hierarchique_poste INTEGER NOT NULL,
    satisfaction_employee_nature_travail INTEGER NOT NULL,
    satisfaction_employee_equipe INTEGER NOT NULL,
    satisfaction_employee_equilibre_pro_perso INTEGER NOT NULL,
    note_evaluation_actuelle INTEGER NOT NULL,
    heure_supplementaires VARCHAR(10) NOT NULL,
    augementation_salaire_precedente VARCHAR(20) NOT NULL,
    a_quitte_l_entreprise VARCHAR(10),
    nombre_participation_pee INTEGER NOT NULL,
    nb_formations_suivies INTEGER NOT NULL,
    nombre_employee_sous_responsabilite INTEGER,
    distance_domicile_travail DOUBLE PRECISION NOT NULL,
    niveau_education INTEGER NOT NULL,
    domaine_etude VARCHAR(100) NOT NULL,
    ayant_enfants VARCHAR(10),
    frequence_deplacement VARCHAR(30) NOT NULL,
    annees_depuis_la_derniere_promotion INTEGER NOT NULL,
    annes_sous_responsable_actuel INTEGER NOT NULL
);

CREATE TABLE prediction_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    employee_id INTEGER NOT NULL,
    endpoint VARCHAR(50) NOT NULL,
    input_payload JSONB NOT NULL,
    output_payload JSONB NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    CONSTRAINT fk_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(id_employee)
);
