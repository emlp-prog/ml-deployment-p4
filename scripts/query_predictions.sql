SELECT id, created_at, employee_id, endpoint, output_payload, model_version
FROM prediction_logs
ORDER BY id DESC
LIMIT 20;

SELECT *
FROM prediction_logs
ORDER BY id DESC
LIMIT 5;
