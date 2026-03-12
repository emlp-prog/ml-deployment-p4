SELECT id, created_at, output_payload->>'prediction' AS prediction
FROM predictions
ORDER BY id DESC
LIMIT 10;

SELECT id, created_at, input_payload, output_payload
FROM predictions
ORDER BY id DESC
LIMIT 5;