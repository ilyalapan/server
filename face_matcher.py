import cv2
import itertools
import os

import openface
import argparse
from color_classification import HistogramColorClassifier

import numpy as np

fileDir = os.path.dirname(os.path.realpath(__file__))
openfaceDir = os.path.join(fileDir, '..', 'openface')
modelDir = os.path.join(openfaceDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

class FaceMatcher:



    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--dlibFacePredictor', type=str, help="Path to dlib's face predictor.",
                            default=os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
        parser.add_argument('--networkModel', type=str, help="Path to Torch network model.",
                            default=os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'))
        parser.add_argument('--imgDim', type=int,
                            help="Default image dimension.", default=96)
        parser.add_argument('--verbose', action='store_true')

        self.args = parser.parse_args()

        self.align = openface.AlignDlib(self.args.dlibFacePredictor)
        self.net = openface.TorchNeuralNet(self.args.networkModel, self.args.imgDim)



    def __getRep(self, imgPath):
        bgrImg = cv2.imread(imgPath)
        if bgrImg is None:
            raise Exception("Unable to load image: {}".format(imgPath))
        rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

        bb = self.align.getLargestFaceBoundingBox(rgbImg)
        if bb is None:
            raise Exception("Unable to find a face: {}".format(imgPath))

        alignedFace = self.align.align(self.args.imgDim, rgbImg, bb,
                                  landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            raise Exception("Unable to align image: {}".format(imgPath))

        rep = self.net.forward(alignedFace)
	
        return rep


    def compare_faces(self, img1, img2):
        d = self.__getRep(img1) - self.__getRep(img2)

        return np.dot(d, d)


    def compare_shoes(self, img_path, database_list):
        classifier = HistogramColorClassifier(channels=[0, 1, 2], hist_size=[128, 128, 128],
                                                 hist_range=[0, 256, 0, 256, 0, 256], hist_type='BGR')
        for data_path in database_list:
            data_img = cv2.imread(data_path)
            classifier.addModelHistogram(data_img)
        img = cv2.imread(img_path)
        comp_array = classifier.returnHistogramComparisonArray(img, method='bhattacharyya')
        return [x for x in comp_array]



