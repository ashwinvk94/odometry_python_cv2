#!/usr/bin/env python2

'''
ENPM 673 Spring 2019: Robot Perception
Project 5 Odometry

Author:
Ashwin Varghese Kuruttukulam(ashwinvk94@gmail.com)
Rachith Prakash (rachithprakash@gmail.com)
Graduate Students in Robotics,
University of Maryland, College Park
'''

import cv2
from ReadCameraModel import ReadCameraModel
import glob
from UndistortImage import UndistortImage
import argparse

__author__ = 'rachith'


def preProcessData(path_to_model, path_to_images):
	'''
	Here, we undistort the dataset images
	:param path_to_model:
	:param path_to_images:
	:return: K - calibration matrix
	'''

	# Read camera parameters
	fx, fy, cx, cy, G_camera_image, LUT = ReadCameraModel(path_to_model)

	# iterate through each image, convert to RGB, undistort(function takes all channels in input)
	images = glob.glob(path_to_images+"/*.png")
	images.sort()
	for cnt, image in enumerate(images):
		frame = cv2.imread(image, -1)
		frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BayerGR2BGR)
		undistorted_image = UndistortImage(frame_RGB, LUT)
		cv2.imwrite(path_to_images + "./undistort/frame" + str(cnt) + ".png", undistorted_image)

	K = [[fx, 0, 0], [0, fy, 0], [cx, cy, 1]]

	return K

def main():

	# Parse input arguments
	Parser = argparse.ArgumentParser()
	Parser.add_argument('--Path', default="./stereo/centre", help='Path to dataset, Default:./stereo/centre')
	Args = Parser.parse_args()
	path = Args.Path

	# Pre-process the data
	preProcessData(path_to_model='./model', path_to_images=path)


if __name__ == "__main__":
	main()