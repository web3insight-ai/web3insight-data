SELECT current_database();

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'data'
  AND table_name = 'actors';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'data'
  AND table_name = 'ecosystems';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'data'
  AND table_name = 'events';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'data'
  AND table_name = 'repos';