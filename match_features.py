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

import glob
import numpy as np
import cv2
from matplotlib import pyplot as plt
import random
import sys
import extractPose
import pre_processing

def getPixelCoordinates(kp1, kp2, matches):
	# Initialize lists
	list_kp1 = []
	list_kp2 = []

	# For each match...
	for mat in matches:
		# Get the matching keypoints for each of the images
		img1_idx = mat.queryIdx
		img2_idx = mat.trainIdx

		# x - columns
		# y - rows
		# Get the coordinates
		(x1, y1) = kp1[img1_idx].pt
		(x2, y2) = kp2[img2_idx].pt

		# Append to each list
		list_kp1.append((x1, y1))
		list_kp2.append((x2, y2))
	return list_kp1, list_kp2


def checkRank2(uncheckedF):
	u, s, vh = np.linalg.svd(uncheckedF)
	if s[-1] != 0:
		s[-1] = 0

	S = np.zeros((s.shape[0], u.shape[0]), dtype=u.dtype)
	np.fill_diagonal(S, s)

	# Re-compute E
	F = u.dot(S).dot(vh)
	return F


def extractMatchFeatures(image1, image2):
	# Initiate SIFT detector
	orb = cv2.ORB_create()

	# find the keypoints and descriptors with SIFT
	kp1, des1 = orb.detectAndCompute(image1, None)
	kp2, des2 = orb.detectAndCompute(image2, None)

	# create BFMatcher object
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

	# Match descriptors.
	matches = bf.match(des1, des2)

	# Sort them in the order of their distance.
	matches = sorted(matches, key=lambda x: x.distance)

	pixelsImg1, pixelsImg2 = getPixelCoordinates(kp1, kp2, matches)

	# img1 = cv2.drawKeypoints(image1, kp1, image1, color=(0, 255, 0), flags=0)
	# img2 = cv2.drawKeypoints(image2, kp2, image2, color=(255, 0, 0), flags=0)
	# cv2.imshow('image1', img1)
	# cv2.imshow('image2', img2)
	# cv2.waitKey(0)

	return pixelsImg1, pixelsImg2


def computeFundamentalMatrix(pixelsImg1, pixelsImg2):
	corMatRow = computeCorrespondMat(pixelsImg1, pixelsImg2)
	u, s, vh = np.linalg.svd(corMatRow)
	# Check Rachith
	v = vh.transpose()
	lastCol = v[:, v.shape[1] - 1]
	return np.vstack((lastCol[0:3], lastCol[3:6], lastCol[6:9]))


def extractImages(path):
	# Read and store all images in the input folder
	filenames = glob.glob(path + "/*.png")
	filenames.sort()
	return filenames


def getRand(pixelsImg1):
	randomPixelInds = []
	while 1:
		randomPixelInd = random.randint(0, len(pixelsImg1) - 1)
		if randomPixelInd not in randomPixelInds:
			randomPixelInds.append(randomPixelInd)
		if len(randomPixelInds) == 4:
			break
	return randomPixelInds


def RANSAC(pixelsImg1, pixelsImg2, epsilonThresh, inlierRatioThresh):
	counter = 1
	while 1:
		randomPixelInds = getRand(pixelsImg1)

		# print randomPixelInds
		randImg1Pixels = []
		randImg2Pixels = []
		for k in randomPixelInds:
			randImg1Pixels.append(pixelsImg1[k])
			randImg2Pixels.append(pixelsImg2[k])
		RandomF = computeFundamentalMatrix(randImg1Pixels, randImg2Pixels)
		# print 'rank before'
		# print np.linalg.matrix_rank(RandomF)		
		RandomF = checkRank2(RandomF)
		# print 'rank after'
		# print np.linalg.matrix_rank(RandomF)		
		inliersInds = []
		for ind in range(len(pixelsImg1)):
			img1Pixels = np.array([pixelsImg1[ind][0], pixelsImg1[ind][1], 1])
			img2Pixels = np.array([pixelsImg2[ind][0], pixelsImg2[ind][1], 1])
			temp = np.matmul(img2Pixels.transpose(), RandomF)
			epsilon = np.matmul(temp, img2Pixels)
			if abs(epsilon) < epsilonThresh:
				inliersInds.append(ind)
		# print epsilon
		# print inliersInds
		inlierPercentage = float(len(inliersInds)) / len(pixelsImg1)
		if inlierPercentage > inlierRatioThresh:
			# print inlierPercentage
			break

	inlierImg1Pixels = []
	inlierImg2Pixels = []
	for k in inliersInds:
		inlierImg1Pixels.append(pixelsImg1[k])
		inlierImg2Pixels.append(pixelsImg2[k])
	inliersF = computeFundamentalMatrix(inlierImg1Pixels, inlierImg2Pixels)

	return inliersF


def computeCorrespondMat(im1Px, im2Px):
	x1, y1 = im1Px[0][0], im1Px[0][1]
	x1_, y1_ = im2Px[0][0], im2Px[0][1]
	mat = np.array([x1 * x1_, x1 * y1_, x1, y1 * x1_, y1 * y1_, y1, x1_, y1_, 1])
	for k in range(1, len(im1Px)):
		x1, y1 = im1Px[k][0], im1Px[k][1]
		x1_, y1_ = im2Px[k][0], im2Px[k][1]
		row = np.array([x1 * x1_, x1 * y1_, x1, y1 * x1_, y1 * y1_, y1, x1_, y1_, 1])
		mat = np.vstack((mat, row))
	return mat


def main(args):
	epsilonThresh = 0.9 #args[2]
	inlierRatioThresh = 0.9 #args[3]

	path = './undistort' #args[0]
	filenames = extractImages(path)

	# Removing first 30 images because it is too bright
	del filenames[:30]
	bgrImages = []

	counter = 0
	for filename in filenames:
		bgrImages.append(cv2.imread(filename, -1))
		counter += 1
		if counter > 100:
			break

	print('done')
	K = pre_processing.extractCalibrationMatrix(path_to_model='./model')

	R = []
	T = []
	for imageIndex in range(len(bgrImages) - 1):
		pixelsImg1, pixelsImg2 = extractMatchFeatures(bgrImages[imageIndex], bgrImages[imageIndex + 1])
		uncheckedF = RANSAC(pixelsImg1, pixelsImg2, epsilonThresh, inlierRatioThresh)
		# print uncheckedF
		# print 'before'
		# print np.linalg.matrix_rank(uncheckedF)
		F = checkRank2(uncheckedF)

	# print np.linalg.matrix_rank(F)
	# 	print F
		t1, r1, t2, r2, t3, r3, t4, r4 = extractPose.extractPose(F, K)

		print(t1)
		print('2')
		print(t2)
		print('3')
		print(t3)
		print('4')
		print(t4)


if __name__ == "__main__":
	main(sys.argv)