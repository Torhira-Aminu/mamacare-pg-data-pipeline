-- How many of the 8 resource types have zero records in each ZIP.
-- IMPORTANT: computed on SYNTHETIC data. This demonstrates the query pattern only;
-- it is NOT evidence of real healthcare access gaps.
SELECT z.zip_code,
       z.city,
       8 - COUNT(DISTINCT r.resource_type) AS types_with_no_records
FROM pg_zip_codes z
LEFT JOIN mamacare_resources r ON r.zip_code = z.zip_code
GROUP BY z.zip_code, z.city
ORDER BY types_with_no_records DESC, z.zip_code;
