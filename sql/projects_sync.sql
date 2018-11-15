SELECT
  project_id
FROM data_warehouse.project_data
WHERE
  project_id = %(project_id)s
;
