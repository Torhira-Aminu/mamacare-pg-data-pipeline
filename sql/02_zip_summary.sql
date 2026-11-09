-- One row per Prince George's County ZIP: total resources and count per type.
-- LEFT JOIN from the ZIP reference table so ZIPs with no records still appear (as 0).
SELECT z.zip_code,
       z.city,
       COUNT(r.resource_id) AS total_resources,
       SUM(CASE WHEN r.resource_type = 'prenatal_clinics' THEN 1 ELSE 0 END) AS prenatal_clinics,
       SUM(CASE WHEN r.resource_type = 'wic_locations' THEN 1 ELSE 0 END) AS wic_locations,
       SUM(CASE WHEN r.resource_type = 'medicaid_resources' THEN 1 ELSE 0 END) AS medicaid_resources,
       SUM(CASE WHEN r.resource_type = 'food_pantries' THEN 1 ELSE 0 END) AS food_pantries,
       SUM(CASE WHEN r.resource_type = 'diaper_banks' THEN 1 ELSE 0 END) AS diaper_banks,
       SUM(CASE WHEN r.resource_type = 'childcare_providers' THEN 1 ELSE 0 END) AS childcare_providers,
       SUM(CASE WHEN r.resource_type = 'transportation_assistance' THEN 1 ELSE 0 END) AS transportation_assistance,
       SUM(CASE WHEN r.resource_type = 'mental_health_services' THEN 1 ELSE 0 END) AS mental_health_services
FROM pg_zip_codes z
LEFT JOIN mamacare_resources r ON r.zip_code = z.zip_code
GROUP BY z.zip_code, z.city
ORDER BY z.zip_code;
