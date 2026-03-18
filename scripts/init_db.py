import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not set in .env")

    sql_path = ROOT / "scripts" / "create_db.sql"
    csv_path = ROOT / "data" / "employee_attrition_dataset.csv"

    dataframe = pd.read_csv(csv_path)

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_path.read_text(encoding="utf-8"))

            insert_query = """
                INSERT INTO employees (
                    id_employee, age, genre, revenu_mensuel, statut_marital, departement, poste,
                    nombre_experiences_precedentes, nombre_heures_travailless, annee_experience_totale,
                    annees_dans_l_entreprise, annees_dans_le_poste_actuel, satisfaction_employee_environnement,
                    note_evaluation_precedente, niveau_hierarchique_poste, satisfaction_employee_nature_travail,
                    satisfaction_employee_equipe, satisfaction_employee_equilibre_pro_perso,
                    note_evaluation_actuelle, heure_supplementaires, augementation_salaire_precedente,
                    a_quitte_l_entreprise, nombre_participation_pee, nb_formations_suivies,
                    nombre_employee_sous_responsabilite, distance_domicile_travail, niveau_education,
                    domaine_etude, ayant_enfants, frequence_deplacement,
                    annees_depuis_la_derniere_promotion, annes_sous_responsable_actuel
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            rows = [tuple(row) for row in dataframe.itertuples(index=False, name=None)]
            cursor.executemany(insert_query, rows)

        connection.commit()

    print("Database initialized successfully.")
    print(f"Employees inserted: {len(dataframe)}")


if __name__ == "__main__":
    main()
