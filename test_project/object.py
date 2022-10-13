import cv2
import numpy as np

#net=cv2.dnn.readNet('yolov3.weights','yolov3.cfg')
net = cv2.dnn.readNetFromDarknet("yolov3-coco/yolov3 (1).cfg", "yolov3-coco/yolov3.weights")
classes = []
with open('coco.names','r') as f:
    classes = f.read().splitlines()
print(classes)    