UPDATE data_warehouse.project_data
SET
  created_at=%(created_at)s
  ,modified_at=%(modified_at)s
  ,state=%(state)s
  ,marked_for_deletion=%(marked_for_deletion)s
  ,flash_id=%(flash_id)s
  ,admin_edit_date=%(admin_edit_date)s
  ,admin_editor=%(admin_editor)s
  ,source_project_id=%(source_project_id)s
  ,customer_id=%(customer_id)s
  ,sku=%(sku)s
  ,page_count=%(page_count)s
  ,photo_boxes=%(photo_boxes)s
  ,photo_boxes_complete=%(photo_boxes_complete)s
  ,gallery_images_uploaded=%(gallery_images_uploaded)s
  ,product_attributes=%(product_attributes)s
  ,price=%(price)s
WHERE
  project_id = %(project_id)s
;
