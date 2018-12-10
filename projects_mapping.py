"""
    encapsulates rules for flattening and mapping DynamoDB document.  
        Custom mappings
        Update `keys` to alter mapping.
        Keys output should match replacement pattern in SQL files
        Flattens DynamoDB stream upate format into standard JSON doc format

    Created for Artifact Uprising
      by: Drew Beaupre - drew@mammothgrowth.com
          Copyright 2018, Mammoth Growth
"""

import dpath.util
import gzip
import io
import zlib
import base64
import simplejson as json
from datetime import datetime
import re
# from boto3.dynamodb.types import TypeDeserializer
  
def strip_currency(value):
  if not value:
    return None

  trim = re.compile(r'[^\d.,]+')
  return trim.sub('', value)

def timestamp_to_datetime(timestamp):
  if not timestamp:
    return None

  return datetime.fromtimestamp(timestamp/1000).isoformat()

def json_to_string(jsonValue):
  if not jsonValue:
    return None
  
  return json.dumps(jsonValue)
  
def page_layers(page):
  if 'layers' in page:
    return page['layers']
  else:
    return []

def filter_layer_type(layer, criteria):
  return 'type' in layer and criteria(layer)
      
def photo_boxes(pages):
  if not pages:
    return []

  return [layer for page in pages for layer in page_layers(page) if filter_layer_type(layer, lambda x: x['type'] == 'user_photo') ]

def photo_boxes_completed(pages):
  if not pages:
    return []

  return [layer for page in pages for layer in page_layers(page) if filter_layer_type(layer, lambda x: x['type'] == 'user_photo' and 'data' in x and 'userPhotoId' in x['data']) ]

def photo_box_count(data):
  if type(data) is list:
    return len(photo_boxes(data))
  else:
    return 0

def photo_box_complete_count(data):
  if type(data) is list:
    return len(photo_boxes_completed(data))
  else:
    return 0

def array_count(data):
  if type(data) is list:
    return len(data)
  else:
    return 0

keys = [
    ("projectId","project_id", None),
    ("createdAt","created_at", timestamp_to_datetime),
    ("modifiedAt","modified_at", timestamp_to_datetime),
    ("state","state", None),
    ("markedForDeletion","marked_for_deletion", None),
    ("user","flash_id", None),
    ("adminEditDate", "admin_edit_date", None),
    ("adminEditor","admin_editor", None),
    ("sourceProjectId", "source_project_id", None),

    ("projectBinaryData/data/user/id", "customer_id", None),
    ("projectBinaryData/data/product/childSku", "sku", None),
    ("projectBinaryData/data/addPhotos/uploadImageCountTotal", "gallery_images_uploaded", None),
    ("projectBinaryData/data/product/attributes", "product_attributes", json_to_string),
    ("projectBinaryData/data/product/magento/price", "price", strip_currency),
    # ("projectBinaryData/data", "project_data", None),

    ("projectBinaryData/data/project/pages", "page_count", array_count),
    ("projectBinaryData/data/project/pages", "photo_boxes", photo_box_count),
    ("projectBinaryData/data/project/pages", "photo_boxes_complete", photo_box_complete_count),

]


def decode_project_binary(gz_data):
    # data = zlib.decompress(gz_data, 16+zlib.MAX_WBITS)

    in_ = io.BytesIO()
    in_.write(base64.b64decode(gz_data))
    in_.seek(0)

    data = gzip.GzipFile(fileobj=in_).read()

    # print("decoding data.... %s " % (data) )
    return json.loads(data)

def flatten_dynamo_document(document):
  

    mapped = {}
    # iterate through document and reduce nested data types
    for key, child in document.items():
        if 'N' in child:
            val = int(child['N'])
        elif 'NULL' in child:
            val = None
        elif 'BOOL' in child:
            val = child['BOOL']
        elif 'S' in child:
            val = child['S']
        else:
          continue
          # raise Exception('Unsupported doucument type in %s' % child)

        if key == 'projectBinaryData' and val:
            val = decode_project_binary(val)

        mapped[key] = val
    
    return mapped

def map(project, decodeBinary=False):
    mapped = {}

    if decodeBinary and project['projectBinaryData']:
      project['projectBinaryData'] = decode_project_binary(project['projectBinaryData'])

    for source_key, target_key, custom_map in keys:
        
        try:

          val = dpath.util.get(project, source_key)
        except KeyError:
          # logger.debug("key %s is missing.  Defaulting to Null" % source_key)
          val = None

        if callable(custom_map):
          val = custom_map(val)

        mapped[target_key] = val

    return mapped

if __name__ == '__main__':

  with open('./project_samples_dynamojson/sample2.json', 'r') as fo:
    project = json.loads(fo.read())

    # mapped = map(project)
    mapped = map(flatten_dynamo_document(project))
    # print("mapped: %s" % mapped)
    with open("output.json", "w") as fo:
        fo.write(json.dumps(mapped))