#!/usr/bin/env python
'''
**********************************************************************
* Filename    : Ultrasonic_Avoidance.py
* Description : A module for SunFounder Ultrasonic Avoidance
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-26    New release
**********************************************************************
'''
import time
import RPi.GPIO as GPIO

class Ultrasonic_Avoidance(object):
	timeout = 0.0005

	def __init__(self, channel):
		self.channel = channel
		GPIO.setmode(GPIO.BCM)

	def distance(self):
	# 	Todo
		pass

def test():
	UA = Ultrasonic_Avoidance(17)
	threshold = 10
	while True:
		distance = UA.get_distance()
		status = UA.less_than(threshold)
		if distance != -1:
			print('distance', distance, 'cm')
			time.sleep(0.2)
		else:
			print(False)
		if status == 1:
			print("Less than %d" % threshold)
		elif status == 0:
			print("Over %d" % threshold)
		else:
			print("Read distance error.")

if __name__ == '__main__':
	test()
