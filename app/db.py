import json
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


class DatabaseError(Exception): # erreur de base de données personnalisée
    pass


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise DatabaseError("DATABASE_URL is not set")

    try:
        return psycopg.connect(database_url, row_factory=dict_row)
    except Exception as exc:
        raise DatabaseError(f"Database connection failed: {exc}") from exc


def get_employee_by_id(employee_id: int):
    query = "SELECT * FROM employees WHERE id_employee = %s"

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (employee_id,))
                employee = cursor.fetchone()
                return employee
    except Exception as exc:
        raise DatabaseError(f"Unable to read employee: {exc}") from exc


def insert_prediction_log(
    employee_id: int,
    endpoint: str,
    input_payload: dict,
    output_payload: dict,
):
    query = """
        INSERT INTO prediction_logs (employee_id, endpoint, input_payload, output_payload, model_version)
        VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
    """

    model_version = os.getenv("MODEL_VERSION", "xgb_pipeline_v1")

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        employee_id,
                        endpoint,
                        json.dumps(input_payload, ensure_ascii=False),
                        json.dumps(output_payload, ensure_ascii=False),
                        model_version,
                    ),
                )
            connection.commit()
    except Exception as exc:
        raise DatabaseError(f"Unable to insert prediction log: {exc}") from exc
