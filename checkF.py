#!/usr/bin/env python2

'''
ENPM 673 Spring 2019: Robot Perception
Project 5: Visual Odometry

Authors:
Ashwin Varghese Kuruttukulam(ashwinvk94@gmail.com)
Rachith Prakash (rachithprakash@gmail.com)
Graduate Students in Robotics,
University of Maryland, College Park
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt


def plotLine(image, a, b, c, fig_num):
	'''
	Function to plot line of an image given the line parameters in the form ax+by+x=0
	:param image:
	:param a:
	:param b:
	:param c:
	:return:
	'''
	plt.imshow(image)
	x = np.linspace(0, image.shape[1], image.shape[1])
	y = - ((a * x) + c) / b
	plt.plot(x, y, linewidth=1.0)
	plt.title(str(fig_num))
	# plt.show()


def calculateEpipoles(F):
	'''
	Function to calculate epipoles using the fundamental matrix
	:param F:
	:return:
	'''

	# left image epipole is the right null-space of the matrix
	# eigen_values, eigen_vectors = np.linalg.eig(F)
	#
	# # sort eigen values decreasing order
	# idx = eigen_values.argsort()[::-1]
	# eigen_values = eigen_values[idx]
	# eigen_vectors = eigen_vectors[:, idx]
	#
	# # get right-eigenvector for left epipole
	# right_eigenvector = eigen_vectors[:, -1]
	# right_eigenvector = right_eigenvector / right_eigenvector[2]

	u, s, vh = np.linalg.svd(F)
	e = vh.T[:, -1]

	return e / e[2]


def isFValid(F, img1_pixels, img2_pixels, image1, image2, fig_num):
	'''
	Function to check if the obtained F is valid or not
	:param F:
	:param img1_pixels:
	:param img2_pixels:
	:return:
	'''

	# for now gives right eigen vector - left epipole
	left_epipole = calculateEpipoles(F)

	for ind in range(len(img2_pixels)):

		try:
			pixel_right = img2_pixels[ind]
			pixel_left = img1_pixels[ind]
			homogeneous_point = np.array([pixel_right[0], pixel_right[1], 1])

			epipolar_line = homogeneous_point.dot(F)

			norm = epipolar_line[0]**2 + epipolar_line[1]**2

			epipolar_line = epipolar_line / norm

			color = tuple([np.random.randint(0, 255) for _ in range(3)])
			cv2.line(image1, (int(np.real(left_epipole[0])), np.real(int(left_epipole[1]))), (int(pixel_left[0]), int(pixel_right[1])), color)

			# plotLine(image1, epipolar_line[0], epipolar_line[1], epipolar_line[2], fig_num)
			#
			# plt.plot(int(pixel_left[0]), int(pixel_left[1]), 'r+')
			# plt.plot(int(np.real(left_epipole[0])), np.real(int(left_epipole[1])), 'b+')
		except OverflowError:
			continue


	# plt.show()