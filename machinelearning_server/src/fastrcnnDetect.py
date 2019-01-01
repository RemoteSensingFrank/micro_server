#!/usr/bin/env python
#-*- coding:utf-8 -*-
import numpy as np
import tensorflow as tf
import os
import io
import string_int_label_map_pb2
from PIL import Image,ImageDraw
from google.protobuf import text_format

#imported data ：
#1.model graph
#2.label mapping 
PATH_TO_FROZEN_GRAPH="D:\\python\\micro_server\\machinelearning_server\\model\\fastrcnn\\frozen_inference_graph.pb" #model graph
PATH_TO_LABEL_MAP="D:\\python\\micro_server\\machinelearning_server\\model\\fastrcnn\\labelmap.pbtxt" #labelmap file

#import label mapping
def _validate_label_map(label_map):
    """Checks if a label map is valid.
    Args:
      label_map: StringIntLabelMap to validate.
    Raises:
      ValueError: if label map is invalid.
    """
    for item in label_map.item:
        if item.id < 0:
            raise ValueError('Label map ids should be >= 0.')
        if (item.id == 0 and item.name != 'background' and
                item.display_name != 'background'):
            raise ValueError('Label map id 0 is reserved for the background label')

def create_category_index(categories):
    """Creates dictionary of COCO compatible categories keyed by category id.
    Args:
      categories: a list of dicts, each of which has the following keys:
        'id': (required) an integer id uniquely identifying this category.
        'name': (required) string representing category name
          e.g., 'cat', 'dog', 'pizza'.
    Returns:
      category_index: a dict containing the same entries as categories, but keyed
        by the 'id' field of each category.
    """
    category_index = {}
    for cat in categories:
        category_index[cat['id']] = cat
    return category_index

def get_max_label_map_index(label_map):
    """Get maximum index in label map.
    Args:
      label_map: a StringIntLabelMapProto
    Returns:
      an integer
    """
    return max([item.id for item in label_map.item])

def convert_label_map_to_categories(label_map,
                                    max_num_classes,
                                    use_display_name=True):
    """Given label map proto returns categories list compatible with eval.
    This function converts label map proto and returns a list of dicts, each of
    which  has the following keys:
      'id': (required) an integer id uniquely identifying this category.
      'name': (required) string representing category name
        e.g., 'cat', 'dog', 'pizza'.
    We only allow class into the list if its id-label_id_offset is
    between 0 (inclusive) and max_num_classes (exclusive).
    If there are several items mapping to the same id in the label map,
    we will only keep the first one in the categories list.
    Args:
      label_map: a StringIntLabelMapProto or None.  If None, a default categories
        list is created with max_num_classes categories.
      max_num_classes: maximum number of (consecutive) label indices to include.
      use_display_name: (boolean) choose whether to load 'display_name' field as
        category name.  If False or if the display_name field does not exist, uses
        'name' field as category names instead.
    Returns:
      categories: a list of dictionaries representing all possible categories.
    """
    categories = []
    list_of_ids_already_added = []
    if not label_map:
        label_id_offset = 1
        for class_id in range(max_num_classes):
            categories.append({
                'id': class_id + label_id_offset,
                'name': 'category_{}'.format(class_id + label_id_offset)
            })
        return categories
    for item in label_map.item:
        if not 0 < item.id <= max_num_classes:
            logging.info(
                'Ignore item %d since it falls outside of requested '
                'label range.', item.id)
            continue
        if use_display_name and item.HasField('display_name'):
            name = item.display_name
        else:
            name = item.name
        if item.id not in list_of_ids_already_added:
            list_of_ids_already_added.append(item.id)
            categories.append({'id': item.id, 'name': name})
    return categories

def load_labelmap(path):
    """Loads label map proto.
    Args:
      path: path to StringIntLabelMap proto text file.
    Returns:
      a StringIntLabelMapProto
    """
    with tf.gfile.GFile(path, 'rb') as fid:
        label_map_string = fid.read()
        label_map = string_int_label_map_pb2.StringIntLabelMap()
        try:
          text_format.Merge(label_map_string, label_map)
        except text_format.ParseError:
          label_map.ParseFromString(label_map_string)
    _validate_label_map(label_map)
    return label_map

def get_label_map_dict(label_map_path,
                       use_display_name=False,
                       fill_in_gaps_and_background=False):
    """Reads a label map and returns a dictionary of label names to id.
    Args:
      label_map_path: path to StringIntLabelMap proto text file.
      use_display_name: whether to use the label map items' display names as keys.
      fill_in_gaps_and_background: whether to fill in gaps and background with
      respect to the id field in the proto. The id: 0 is reserved for the
      'background' class and will be added if it is missing. All other missing
      ids in range(1, max(id)) will be added with a dummy class name
      ("class_<id>") if they are missing.
    Returns:
      A dictionary mapping label names to id.
    Raises:
      ValueError: if fill_in_gaps_and_background and label_map has non-integer or
      negative values.
    """
    label_map = load_labelmap(label_map_path)
    label_map_dict = {}
    for item in label_map.item:
        if use_display_name:
            label_map_dict[item.display_name] = item.id
        else:
            label_map_dict[item.name] = item.id

    if fill_in_gaps_and_background:
        values = set(label_map_dict.values())

        if 0 not in values:
            label_map_dict['background'] = 0
        if not all(isinstance(value, int) for value in values):
            raise ValueError('The values in label map must be integers in order to'
                          'fill_in_gaps_and_background.')
        if not all(value >= 0 for value in values):
            raise ValueError('The values in the label map must be positive.')

        if len(values) != max(values) + 1:
            # there are gaps in the labels, fill in gaps.
            for value in range(1, max(values)):
                if value not in values:
                    label_map_dict['class_' + str(value)] = value

    return label_map_dict

def create_categories_from_labelmap(label_map_path, use_display_name=True):
    """Reads a label map and returns categories list compatible with eval.
    This function converts label map proto and returns a list of dicts, each of
    which  has the following keys:
      'id': an integer id uniquely identifying this category.
      'name': string representing category name e.g., 'cat', 'dog'.
    Args:
      label_map_path: Path to `StringIntLabelMap` proto text file.
      use_display_name: (boolean) choose whether to load 'display_name' field
        as category name.  If False or if the display_name field does not exist,
        uses 'name' field as category names instead.
    Returns:
      categories: a list of dictionaries representing all possible categories.
    """
    label_map = load_labelmap(label_map_path)
    max_num_classes = max(item.id for item in label_map.item)
    return convert_label_map_to_categories(label_map, max_num_classes,
                                          use_display_name)

def create_category_index_from_labelmap(label_map_path, use_display_name=True):
    """Reads a label map and returns a category index.
    Args:
      label_map_path: Path to `StringIntLabelMap` proto text file.
      use_display_name: (boolean) choose whether to load 'display_name' field
        as category name.  If False or if the display_name field does not exist,
        uses 'name' field as category names instead.
    Returns:
      A category index, which is a dictionary that maps integer ids to dicts
      containing categories, e.g.
      {1: {'id': 1, 'name': 'dog'}, 2: {'id': 2, 'name': 'cat'}, ...}
    """
    categories = create_categories_from_labelmap(label_map_path, use_display_name)
    return create_category_index(categories)

def create_class_agnostic_category_index():
    """Creates a category index with a single `object` class."""
    return {1: {'id': 1, 'name': 'object'}}

#import labelmapping 
#param path:label mapping file path
def loadTfLabelMap(path):
    """Loads label map proto.
    Args:
      path: path to StringIntLabelMap proto text file.
    Returns:
      a StringIntLabelMapProto
    """
    with tf.gfile.GFile(path, 'r') as fid:
        label_map_string = fid.read()
        label_map = string_int_label_map_pb2.StringIntLabelMap()
        try:
            text_format.Merge(label_map_string, label_map)
        except text_format.ParseError:
            label_map.ParseFromString(label_map_string)
    _validate_label_map(label_map)
    return label_map

###########################################################################################

#import model graph
""" def loadTfGraph(path):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(path, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='fast-rcnn')

    return detection_graph
 """

#trans image into numpy data
#param image:image obj
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

"""
FastRCNNDetector:
initial with:graph path and labelmap path
if the param do not provided it will use the default params
"""
class FastRCNNDetector:
    def __init__(self, *args, **kwargs):
        pathMap  = PATH_TO_LABEL_MAP
        pathGraph= PATH_TO_FROZEN_GRAPH
        if(len(args)==1):
          pathGraph=args[0]
        if(len(args)==2):
          pathGraph=args[0]
          pathMap  =args[1]

        self.detection_graph = tf.Graph()
        self.labelMap = create_category_index_from_labelmap(PATH_TO_LABEL_MAP,use_display_name=True)
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

    #recongnize
    #param image:image object
    #param graph:model graph
    def run_inference_for_single_image(self,image):
        with self.detection_graph.as_default():
            with tf.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                #print(all_tensor_names)
                tensor_dict = {}
                keys=['num_detections','detection_boxes','detection_scores','detection_classes','detection_masks']
                for key in keys:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
                if 'detection_masks' in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)

                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
                # Run inference
                output_dict = sess.run(tensor_dict,
                                    feed_dict={image_tensor: np.expand_dims(image, 0)})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                    'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
        return output_dict

    #detector wapper as path
    #param pathImg:image path
    #param graph:model graphic
    def target_detect(self,pathImg):
        image = Image.open(pathImg)
        image_np = load_image_into_numpy_array(image)
        image_np_expanded = np.expand_dims(image_np, axis=0)
        output_dict = self.run_inference_for_single_image(image_np, self.detection_graph)
        return output_dict

    #imput binnary data of the image and detected
    #param imgBuf:image binnary data
    #param graph :model graph
    #param labelMap:laebl of the map
    def target_detect_binnary(self,imgBuf):
        f=io.BytesIO(imgBuf)
        image=Image.open(f)
        image_np = load_image_into_numpy_array(image)
        image_np_expanded = np.expand_dims(image_np, axis=0)
        output_dict = self.run_inference_for_single_image(image_np, self.detection_graph)
        return output_dict

    #detector as output as visiual
    #param pathImg:image path
    #param thresthold:reliable thresthold
    def target_detect_visiual_output(self,pathImg,thresthold):
        output=self.target_detect(pathImg)
        boxes = output['detection_boxes']
        scores = output['detection_scores']
        classes = output['detection_classes']
        img = Image.open(pathImg)
        (im_width, im_height) = img.size
        visiual_output=[]
        for idx,score in enumerate(scores):
            outputItem={}
            if score>thresthold:
                  outputItem['box']=(boxes[idx][0]*im_width,boxes[idx][2]*im_height,boxes[idx][1]*im_width,boxes[idx][3]*im_height)
                  outputItem['score']=score
                  outputItem['classify']=""
                  for idxclass,itemid in enumerate(labelMap):
                      if(labelMap[itemid]["id"]==classes[idx]):
                          outputItem['classify']=labelMap[itemid]["name"]
                          break
                  visiual_output.append(outputItem)
                  pass
        return visiual_output

    #detector as output as visiual
    #param pathImg:image path
    #param labelMap:classify label
    #param thresthold:reliable thresthold
    def target_detect_visiual_binnary(self,imgBuf,thresthold):
        output=self.target_detect(imgBuf)
        boxes = output['detection_boxes']
        scores = output['detection_scores']
        classes = output['detection_classes']
        f=io.BytesIO(imgBuf)
        img=Image.open(f)
        (im_width, im_height) = img.size
        visiual_output=[]
        for idx,score in enumerate(scores):
            outputItem={}
            if score>thresthold:
                  outputItem['box']=(boxes[idx][0]*im_width,boxes[idx][2]*im_height,boxes[idx][1]*im_width,boxes[idx][3]*im_height)
                  outputItem['score']=score
                  outputItem['classify']=""
                  for idxclass,itemid in enumerate(labelMap):
                      if(labelMap[itemid]["id"]==classes[idx]):
                          outputItem['classify']=labelMap[itemid]["name"]
                          break
                  visiual_output.append(outputItem)
                  pass
        return visiual_output
