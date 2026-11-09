-- Resource counts per ZIP code and resource type (SYNTHETIC data).
SELECT zip_code, resource_type, COUNT(*) AS resource_count
FROM mamacare_resources
GROUP BY zip_code, resource_type
ORDER BY zip_code, resource_type;
