#!/usr/bin/env python3

import subprocess

class isoSPI:
	"""Handels the isoSPI transactions."""

	# LTC3300-1 ---------------------------------
	# SPI Specifications
	_BALANCE_CMD_PEC_BYTES = 1
	_BALANCE_DATA_PEC_BYTES = 2
	_BALANCE_PEC_BITS = 4

	# CRC4
	_CRC4_POLY = 0x13		# Polynomial for the CRC4

	# LTC6813-1 ---------------------------------
	# SPI Specifications
	_CMD_BYTES = 2
	_PEC_BYTES = 2
	_DATA_BYTES = 6

	# CRC15
	_CRC15_INIT = 0x0010	# Initial Value for the CRC15
	_CRC15_POLY = 0xC599 	# Polynomial for the CRC15

	# Raspberry Pi Pinout (BOARD) ---------------
	# Pins
	_MOSI = 19
	_MISO = 21
	_CLK = 32
	_CE0 = 24
	_CE1 = 26

	def __init__(self):
		self.line = 0
		pass

	def xfer(self, spi, boards, cmd, data=[], error_check=True):
		"""Returns the result or None in case of a connection error."""
		tx = ['/home/pi/cc/isoSPI', str(self.line), str(spi), str(boards), str(cmd)]
		for d in data:
			tx.append(str(d))

		error = True
		count = 1
		while error:
			error = False
			if count > 2:
				return None
			elif count == 2:
				self.line ^= 1
				tx[1] = str(self.line)
			count += 1

			res = subprocess.run(tx, stdout=subprocess.PIPE)
			stdout = res.stdout.decode('utf-8')
			length = int(len(stdout) / 16)
			rx = []
			for i in range(length):
				msg = int(stdout[i*16:(i+1)*16], 16)
				if msg == 0xffffffffffffffff and error_check: # Connection error
					error = True
				rx.append(msg)
		return rx

	def rx(self, boards, cmd):
		"""Returns the valid content of a register (in a list) or None."""
		pec = self.calc_CRC15(cmd, isoSPI._CMD_BYTES)
		cmd = (cmd << isoSPI._PEC_BYTES*8) + pec
		data = [0x0] * boards

		rx = self.xfer(0, boards, cmd, data)
		if rx is None:
			return None

		payload = []
		for msg in rx:
			dat = self.check_CRC15(msg, isoSPI._DATA_BYTES+isoSPI._PEC_BYTES)
			if dat is not None:
				payload.append(dat)
			else:
				return None
		return payload

	def tx(self, spi, boards, cmd, data):
		"""Transmits a command and additional data if required."""
		pec = self.calc_CRC15(cmd, isoSPI._CMD_BYTES)
		cmd = (cmd << isoSPI._PEC_BYTES*8) + pec
		for i, dat in enumerate(data):
			pec = self.calc_CRC15(dat, isoSPI._DATA_BYTES)
			data[i] = (dat << isoSPI._PEC_BYTES*8) + pec
		return self.xfer(spi, boards, cmd, data) # Returns because of SPI

	def spi(self, spi, boards, cmd, payload, parity, crc, ICOM, FCOM):
		"""Performs an SPI transaction between the LTC6813-1 and the LTC3300-1.
		
		Formal parameters:
		payload -- [balance_cmd, balance_data]
		"""
		if parity:
			balance_cmd = payload[0] | self.calc_even_parity(payload[0], isoSPI._BALANCE_CMD_PEC_BYTES)
		else:
			balance_cmd = payload[0]
		if crc:
			balance_data = (payload[1] << isoSPI._BALANCE_PEC_BITS) | self.calc_CRC4(payload[1])
		else:
			balance_data = payload[1]
		dat = ICOM[0] << 44 | balance_cmd << 36 | FCOM[0] << 32
		dat |= ICOM[1] << 28 | (balance_data & 0xff00) << 12 | FCOM[1] << 16
		dat |= ICOM[2] << 12 | (balance_data & 0xff) << 4 | FCOM[2]
		data = [dat] * boards
		rx = self.tx(spi, boards, cmd, data)
		return rx

	def calc_even_parity(self, data, bytes_):
		"""Calculates the even parity bit for the given data and returns it."""
		n = 0
		for i in range(bytes_*8):
			if data & (1 << i):
				n += 1
		if (n % 2) == 0:
			return 0
		return 1

	def check_even_parity(self, message, bytes_):
		"""Checks if message[7..0] is even parity."""
		if not self.calc_even_parity(message, bytes_):
			return True
		return False

	def bin_length(self, value, bytes_):
		"""Returns the number of bits necessary to represent value, if value can be represented with n bytes_."""
		n = 0
		for i in range(bytes_*8):
			if value & (1 << i):
				n = i
		return n + 1

	def calc_CRC4(self, data):
		"""Calculates the inverted 4-bit CRC for the given data[15..4] and returns it."""
		divisor = isoSPI._CRC4_POLY
		data <<= 4
		length = self.bin_length(data, 2)
		while length >= 5:
			data ^= (divisor << (length - 5))
			length = self.bin_length(data, 2)
		return 15 - data

	def check_CRC4(self, message):
		"""Checks if the inverted 4-bit CRC (message[3..0]) of the given message[15..4] is correct."""
		data = (message & 0xfff0) >> 4
		crc = message & 0xf
		if crc == self.calc_CRC4(data):
			return data
		return None

	def calc_CRC15(self, data, bytes_):
		"""Calculates the 16-bit CRC for the given data and number of bytes_ (min. 2) and returns it."""
		divisor = isoSPI._CRC15_POLY
		mask_init = isoSPI._CRC15_INIT << (1 + (bytes_-2)*8)
		data = (data ^ mask_init) << 15
		length = self.bin_length(data, bytes_+2)
		while length >= 16:
			data ^= (divisor << (length - 16))
			length = self.bin_length(data, bytes_+2)
		return data << 1

	def check_CRC15(self, message, bytes_):
		"""Checks if the 16-bit CRC (message[15..0]) of the given message[(bytes_*8 - 1)..16] is correct."""
		data_mask = (2**((bytes_-2)*8) - 1) << 16
		data = (message & data_mask) >> 16
		crc = message & 0xffff
		if crc == self.calc_CRC15(data, bytes_-2):
			return data
		return None

def main():
	pass

if __name__ == "__main__":
	main()
