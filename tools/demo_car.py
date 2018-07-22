#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
import _init_paths

from model.config import cfg
from model.test import im_detect
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
import numpy as np
import os, cv2
import csv
import time
from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',),'res101': ('res101_faster_rcnn_iter_20000.ckpt',)}

DATASETS= {'carcar':('carcar_2018_trainval',)}

CLASSES = ('__background__', 'car')
IMG_DIR = '/content/tf-faster-rcnn/data/images'
def output_detect(im, class_name, dets, thresh=0.5):
    l_out = []
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        rect =  (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
        l_out.append(rect)
    return l_out

def img_detect(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""
    # Load the demo image
    im_file = os.path.join(IMG_DIR, image_name)
    im = cv2.imread(im_file)
    if im is None:
        return None
    
    scores, boxes = im_detect(sess, net, im)

    l_out =[]
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]): #only return the second class output , 'car'
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        l_out = output_detect(im, cls, dets, thresh=CONF_THRESH)
    return l_out

def load_img_list(path):
    img_list = []
    with open(path) as csv_file:
        fields = ['name']
        reader = csv.DictReader(csv_file, fieldnames=fields)
        for row in reader:
            img = row['name']
            img_list.append(img)
    return img_list

def img_batch_detect(path):
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals


    demonet = 'res101'
    dataset = 'carcar'
    tfmodel = os.path.join('output', demonet, DATASETS[dataset][0],
                           NETS[demonet][0])
    if not os.path.isfile(tfmodel + '.meta'):
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True


    # init session
    sess = tf.Session(config=tfconfig)
    net = resnetv1(num_layers=101)

    net.create_architecture("TEST", 2,
                            tag='default', anchor_scales=[8, 16, 32])

    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))

    #load all images
    im_names = load_img_list(path)
    out_detect = []

    #detect all images, print time every 100 pics
    count = 0
    start = time.time()
    for im_name in im_names:
        if count % 100 == 0:
            end = time.time()
            print('detect time for 100 pics: {}'.format(end-start))
            start = end
        l_out = img_detect(sess, net, im_name)
        out_detect.append((im_name, l_out))
        count = count + 1

     #write out to out.csv
    write_to_csv('out_detect.csv',out_detect)

def write_to_csv(path, list_out):
    print(len(list_out))
    with open(path, 'a') as out_csv:
        fields = ['image_name', 'rois']
        for i in range(len(list_out)):
            r = list_out[i]
            writer = csv.DictWriter(out_csv, fieldnames=fields)
            writer.writerow({'image_name': r[0], 'rois': r[1]})

img_batch_detect('test_a.csv')
