#!/usr/bin/env python3

from math import sin, pi
from time import time

class SunnyBoy():
	"""Models the battery inverter "Sunny Boy Storage 2.5"."""

	def __init__(self, period):
		self.period = period
		self.running = True
		self.current = 0

	def start(self):
		"""Sets the state to True."""
		self.running = True

	def stop(self):
		"""Sets the state to False."""
		self.running = False

	def get_state(self):
		"""Returns the current state."""
		return self.running

	def get_current_A(self):
		'''Returns the amperage.
		A positive amperage corresponds to charging and a negative amperage corresponds to discharging.
		'''
		if self.running:
			self.current = 10 * sin(2 * pi / self.period * time())
		else:
			self.current = 0
		return self.current

def main():
	pass

if __name__ == "__main__":
	main()
