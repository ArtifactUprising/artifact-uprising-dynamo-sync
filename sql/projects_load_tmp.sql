
create table #project_data_import
(
	project_id varchar(256),
	created_at timestamp,
	modified_at timestamp,
	state varchar(256),
	marked_for_deletion boolean,
	flash_id varchar(256),
	admin_edit_date timestamp,
	admin_editor varchar(256),
	source_project_id varchar(256),
	customer_id bigint,
	sku varchar(256),
	page_count integer,
	photo_boxes integer,
	photo_boxes_complete integer,
	gallery_images_uploaded integer,
	product_attributes varchar(65535),
	price numeric(12,4)
)
;

INSERT INTO #project_data_import
(project_id
,created_at
,modified_at
,state
,marked_for_deletion
,flash_id
,admin_edit_date
,admin_editor
,source_project_id
,customer_id
,sku
,page_count
,photo_boxes
,photo_boxes_complete
,gallery_images_uploaded
,product_attributes
,price
)
VALUES
%s
;



begin;

-- DELETE FROM data_warehouse.project_data
--   USING #project_data_import imp
--   WHERE 
--     data_warehouse.project_data.project_id = imp.project_id
--     --Ignore any late updates
--     AND data_warehouse.project_data.modified_at < imp.modified_at
--     ;

-- -- Delete anything that wasn't removed
-- DELETE FROM #project_data_import
--     USING data_warehouse.project_data cur
-- WHERE #project_data_import.project_id = cur.project_id
-- ;


UPDATE data_warehouse.project_data
SET
  created_at=imp.created_at
  ,modified_at=imp.modified_at
  ,state=imp.state
  ,marked_for_deletion=imp.marked_for_deletion
  ,flash_id=imp.flash_id
  ,admin_edit_date=imp.admin_edit_date
  ,admin_editor=imp.admin_editor
  ,source_project_id=imp.source_project_id
  ,customer_id=imp.customer_id
  ,sku=imp.sku
  ,page_count=imp.page_count
  ,photo_boxes=imp.photo_boxes
  ,photo_boxes_complete=imp.photo_boxes_complete
--   ,gallery_images_uploaded=imp.gallery_images_uploaded
  ,product_attributes=imp.product_attributes
  ,price=imp.price
FROM (
    SELECT 
        *, 
        -- Only insert latest in batch
        row_number() OVER(PARTITION BY project_id ORDER BY modified_at DESC) as rn
    FROM #project_data_import
    ) imp
WHERE
    data_warehouse.project_data.project_id = imp.project_id
    AND data_warehouse.project_data.modified_at <= imp.modified_at
    AND rn = 1
;


INSERT INTO data_warehouse.project_data
(project_id
,created_at
,modified_at
,state
,marked_for_deletion
,flash_id
,admin_edit_date
,admin_editor
,source_project_id
,customer_id
,sku
,page_count
,photo_boxes
,photo_boxes_complete
-- ,gallery_images_uploaded
,product_attributes
,price
)
WITH projects AS(
    SELECT 
        *, 
        -- Only insert latest in batch
        row_number() OVER(PARTITION BY project_id ORDER BY modified_at DESC) as rn
    FROM #project_data_import
)

SELECT
project_id
,created_at
,modified_at
,state
,marked_for_deletion
,flash_id
,admin_edit_date
,admin_editor
,source_project_id
,customer_id
,sku
,page_count
,photo_boxes
,photo_boxes_complete
-- ,gallery_images_uploaded
,product_attributes
,price
FROM projects imp
WHERE rn = 1
AND NOT EXISTS(SELECT project_id from data_warehouse.project_data WHERE project_id = imp.project_id)
;

commit;

end;