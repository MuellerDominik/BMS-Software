#!/usr/bin/env python3

import dev_spidev as spidev
# import spidev

class isoSPI:
	'''
	LTC3300-1
	'''
	# Address
	_ADDR = 0b10101000		# Fixed Internal Address

	# CMD (Command Bits)
	_WBC = 0b000			# Write Balance Command
	_RBC = 0b010			# Readback Balance Command
	_RBS = 0b100			# Read Balance Status
	_EBC = 0b110			# Execute Balance Command

	# DATA[15..4] in chunks of 2-bit (Cell Balancer Control Bits)
	# Chunks must be shifted to the right position: (6 - n)*2 + 4
	_DBCn = 0b00			# None (Disable Balancing Cell n)
	_DCnN = 0b01			# Discharge Cell n (Nonsynchronous)
	_DCnS = 0b10			# Discharge Cell n (Synchronous)
	_CCn = 0b11				# Charge Cell n

	# CRC4
	_CRC4_POLY = 0x13		# Polynomial for the CRC4

	'''
	LTC6813-1
	'''
	# CRC15
	_CRC15_INIT = 0x0010	# Initial Value for the CRC15
	_CRC15_POLY = 0xC599 	# Polynomial for the CRC15

	def __init__(self, bus, device, spi_freq=488000, spi_mode=0b00):
		self.spi = spidev.SpiDev()
		self.bus = bus
		self.device = device
		self.spi.max_speed_hz = spi_freq
		self.spi.mode = spi_mode

	def xfer(self, *argv):
		data = []
		for pkg in argv:
			for i in range(pkg[1]-1, -1, -1):
				data.append((pkg[0] & (0xff << i*8)) >> i*8)
			PEC = self.calc_CRC15(pkg[0], pkg[1])
			PEC0 = (PEC & 0xff00) >> 8
			PEC1 = PEC & 0xff
			data.extend([PEC0, PEC1])

		self.spi.open(self.bus, self.device)
		rx = self.spi.xfer2(data)
		self.spi.close()
		return rx

	def calc_even_parity(self, DATA, BYTES):
		"""Calculates the even parity bit for the given DATA and returns it."""
		n = 0
		for i in range(BYTES*8):
			if DATA & (1 << i):
				n += 1
		if (n % 2) == 0:
			return 0
		return 1

	def is_even_parity(self, MESSAGE, BYTES):
		"""Checks if MESSAGE[7..0] is even parity."""
		if not self.calc_even_parity(MESSAGE, BYTES):
			return True
		return False

	def bin_length(self, VALUE, BYTES):
		"""Returns the number of bits necessary to represent VALUE, if VALUE can be represented with n BYTES."""
		n = 0
		for i in range(BYTES*8):
			if VALUE & (1 << i):
				n = i
		return n + 1

	def calc_CRC4(self, DATA):
		"""Calculates the inverted 4-bit CRC for the given DATA[15..4] and returns it."""
		divisor = isoSPI._CRC4_POLY
		DATA <<= 4
		length = self.bin_length(DATA, 2)
		while length >= 5:
			DATA ^= (divisor << (length - 5))
			length = self.bin_length(DATA, 2)
		return 15 - DATA

	def check_CRC4(self, MESSAGE):
		"""Checks if the inverted 4-bit CRC (MESSAGE[3..0]) of the given MESSAGE[15..4] is correct."""
		DATA = (MESSAGE & 0xfff0) >> 4
		CRC = MESSAGE & 0xf
		if CRC == self.calc_CRC4(DATA):
			return True
		return False

	def calc_CRC15(self, DATA, BYTES):
		"""Calculates the 16-bit CRC for the given DATA and number of BYTES (min. 2) and returns it."""
		divisor = isoSPI._CRC15_POLY
		MASK_INIT = isoSPI._CRC15_INIT << (1 + (BYTES-2)*8)
		DATA = (DATA ^ MASK_INIT) << 15
		length = self.bin_length(DATA, BYTES+2)
		while length >= 16:
			DATA ^= (divisor << (length - 16))
			length = self.bin_length(DATA, BYTES+2)
		return DATA << 1

	def check_CRC15(self, MESSAGE, BYTES):
		"""Checks if the 16-bit CRC (MESSAGE[15..0]) of the given MESSAGE[(BYTES*8 - 1)..16] is correct."""
		DATA_MASK = (2**((BYTES-2)*8) - 1) << 16
		DATA = (MESSAGE & DATA_MASK) >> 16
		CRC = MESSAGE & 0xffff
		if CRC == self.calc_CRC15(DATA, BYTES-2):
			return True
		return False

def main():
	"""Debug."""
	isoSPI1 = isoSPI(0, 0)
	data = isoSPI1.xfer((0x0001, 2), (0xff9baafffa, 5))
	string = "["
	for val in data:
		string += hex(val) + ", "
	print(string[0:-2] + "]")
	print(isoSPI1.check_CRC15(0xff9baafffa2c68, 7))

	x = 0b110000010000
	y = 0b1010111
	z = 0x0001

	print("---")

	print(bin(isoSPI1.calc_CRC4(x)))
	print(isoSPI1.check_CRC4((x << 4) + isoSPI1.calc_CRC4(x)))

	print("---")

	print(bin((y << 1) + isoSPI1.calc_even_parity(y, 1)))
	print(isoSPI1.is_even_parity((y << 1) + isoSPI1.calc_even_parity(y, 1), 1))

	print("---")

	print(hex(isoSPI1.calc_CRC15(z, 2)))
	print(isoSPI1.check_CRC15((z << 16) + isoSPI1.calc_CRC15(z, 2), 4))

	print("---")

if __name__ == "__main__":
	main()
