#!/usr/bin/env python3

from classes.SunnyBoy import SunnyBoy
from classes.isoSPI import isoSPI
from math import sqrt

class BMS():
	"""Models the battery management system."""

	# General Specifications --------------------
	_BLOCKS_PER_BOARD = 6	# Prototype BMS-Board handles six blocks

	# LTC6813-1 ---------------------------------
	# Commands
	_WRCFGA = 0x0001		# Write Configuration Register Group A
	_WRCFGB = 0x0024		# Write Configuration Register Group B
	_RDCFGA = 0x0002		# Read Configuration Register Group A
	_RDCFGB = 0x0026		# Read Configuration Register Group B
	_RDCVA = 0x0004			# Read Cell Voltage Register Group A
	_RDCVB = 0x0006			# Read Cell Voltage Register Group B
	_RDCVC = 0x0008			# Read Cell Voltage Register Group C
	_RDCVD = 0x000a			# Read Cell Voltage Register Group D
	_RDCVE = 0x0009			# Read Cell Voltage Register Group E
	_RDCVF = 0x000b			# Read Cell Voltage Register Group F
	_RDAUXA = 0x000c		# Read Auxiliary Register Group A
	_RDAUXB = 0x000e		# Read Auxiliary Register Group B
	_RDAUXC = 0x000d		# Read Auxiliary Register Group C
	_RDAUXD = 0x000f		# Read Auxiliary Register Group D
	_RDSTATA = 0x0010		# Read Status Register Group A
	_RDSTATB = 0x0012		# Read Status Register Group B
	_WRSCTRL = 0x0014		# Write S Control Register Group
	_WRPWM = 0x0020			# Write PWM Register Group
	_WRPSB = 0x001c			# Write PWM/S Control Register Group B
	_RDSCTRL = 0x0016		# Read S Control Register Group
	_RDPWM = 0x0022			# Read PWM Register Group
	_RDPSB = 0x001e			# Read PWM/S Control Register Group B
	_STSCTRL = 	0x0019		# Start S Control Pulsing and Poll Status
	_CLRSCTRL = 0x0018		# Clear S Control Register Group

	# Not Complete (see Configuration below)
	_ADCV = 0x0260			# Start Cell Voltage ADC Conversion and Poll Status
	_ADOW = 0x0228			# Start Open Wire ADC Conversion and Poll Status
	_CVST = 0x0207			# Start Self Test Cell Voltage Conversion and Poll Status
	_ADOL = 0x0201			# Start Overlap Measurements of Cell 7 and Cell 13 Voltages
	_ADAX = 0x0460			# Start GPIOs ADC Conversion and Poll Status
	_ADAXD = 0x0400			# Start GPIOs ADC Conversion with Digital Redundancy and Poll Status
	_AXOW = 0x0410			# Start GPIOs Open Wire ADC Conversion and Poll Status
	_AXST = 0x0407			# Start Self Test GPIOs Conversion and Poll Status
	_ADSTAT = 0x0468		# Start Status Group ADC Conversion and Poll Status
	_ADSTATD = 0x0408		# Start Status Group ADC Conversion with Digital Redundancy and Poll Status
	_STATST = 0x040f		# Start Self Test Status Group Conversion and Poll Status
	_ADCVAX = 0x046f		# Start Combined Cell Voltage and GPIO1, GPIO2 Conversion and Poll Status
	_ADCVSC = 0x0467		# Start Combined Cell Voltage and SC Conversion and Poll Status

	# Start Configuration -----------------------

	# MD[1:0] - ADC Mode [ADCOPT(CFGAR0[0]) = 0 | ADCOPT(CFGAR0[0]) = 1]
	_MD_422_1k = 0x00		# 422Hz Mode | 1kHz Mode
	_MD_Fast_14k = 0x0080	#  27kHz Mode (Fast) | 14kHz Mode
	_MD_Normal_3k = 0x0100	# 7kHz Mode (Normal)  | 3kHz Mode
	_MD_Filt_2k = 0x0180	# 26Hz Mode (Filtered) | 2kHz Mode

	# DCP - Discharge Permitted
	_DCP_NP = 0x0000		# Discharge Not Permitted
	_DCP_P = 0x0010			# Discharge Permitted

	# CH[2:0] - Cell Selection for ADC Conversion
	_CH_All = 0x0000		# All Cells
	_CH_1_7_13 = 0x0001		# Cells 1, 7, 13
	_CH_2_8_14 = 0x0002		# Cells 2, 8, 14
	_CH_3_9_15 = 0x0003		# Cells 3, 9, 15
	_CH_4_10_16 = 0x0004	# Cells 4, 10, 16
	_CH_5_11_17 = 0x0005	# Cells 5, 11, 17
	_CH_6_12_18 = 0x0006	# Cells 6, 12, 18

	# PUP - Pull-Up/Pull-Down Current for Open Wire Conversions
	_PUP_PD = 0x0000		# Pull-Down Current
	_PUP_PU = 0x0040		# Pull-Up Current

	# ST[1:0] - Self Test Mode Selection
	_ST_1 = 0x0020			# Self Test 1
	_ST_2 = 0x0040			# Self test 2

	# Self Test Conversion Results
	_STR1_27k = 0x9565		# Self Test 1: 27kHz
	_STR2_27k = 0x6A9A		# Self Test 2: 27kHz
	_STR1_14k =  0x9553		# Self Test 1: 14kHz
	_STR2_14k = 0x6AAC		# Self Test 2: 14kHz
	_STR1_Rem = 0x9555		# Self Test 1: 7kHz / 3kHz / 2kHz / 1kHz / 422Hz / 26Hz
	_STR2_Rem = 0x6AAA		# Self Test 2: 7kHz / 3kHz / 2kHz / 1kHz / 422Hz / 26Hz

	# CHG[2:0] - GPIO Selection for ADC Conversion
	_CHG_All = 0x0000		# GPIO 1–5, 2nd Reference, GPIO 6–9
	_CHG_1_6 = 0x0001		# GPIO 1 and GPIO 6
	_CHG_2_7 = 0x0002		# GPIO 2 and GPIO 7
	_CHG_3_8 = 0x0003		# GPIO 3 and GPIO 8
	_CHG_4_9 = 0x0004		# GPIO 4 and GPIO 9
	_CHG_5 = 0x0005			# GPIO 5
	_CHG_Ref = 0x0006		# 2nd Reference

	# CHST[2:0] - Status Group Selection
	_CHST_All = 0x0000		# SC, ITMP, VA, VD
	_CHST_SC = 0x0001		# SC
	_CHST_ITMP = 0x0002		# ITMP
	_CHST_VA = 0x0003		# VA
	_CHST_VD = 0x0004		# VD

	# Write Codes for ICOMn[3:0] and FCOMn[3:0] on SPI Master
	# ICOMn[3:0]
	_CSBM_Low = 0b1000		# CSBM Low - Generates a CSBM Low Signal on SPI Port (GPIO3)
	_CSBM_Falling = 0b1010	# CSBM Falling Edge - Drives CSBM (GPIO3) High, then Low
	_CSBM_High = 0b1001		# CSBM High - Generates a CSBM High Signal on SPI Port (GPIO3)
	_STOP_Trans = 0b1111	# No Transmit - Releases the SPI Port and Ignores the Rest of the Data

	# FCOMn[3:0] - (Already defined, see ICOMn[3:0])
	# _CSBM_Low = 0b1000	# CSBM Low - Holds CSBM Low at the End of Byte Transmission (MSB irrelevant)
	# _CSBM_High = 0b1001	# CSBM High - Transitions CSBM High at the End of Byte Transmission

	# End Configuration -------------------------

	_CLRCELL = 0x0711		# Clear Cell Voltage Register Groups
	_CLRAUX = 0x0712		# Clear Auxiliary Register Groups
	_CLRSTAT = 0x0713		# Clear Status Register Groups
	_PLADC = 0x0714			# Poll ADC Conversion Status
	_DIAGN = 0x0715 		# Diagnose MUX and Poll Status
	_WRCOMM = 0x0721		# Write COMM Register Group
	_RDCOMM = 0x0722		# Read COMM Register Group
	_STCOMM = 0x0723		# Start I2C/SPI Communication
	_MUTE = 0x0028			# Mute Discharge
	_UNMUTE = 0x0029		# Unmute Discharge

	# LTC3300-1 ---------------------------------
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

	# PT1000 - ITS-90 ---------------------------
	_POLY_A = 3.9083e-3
	_POLY_B = -5.7750e-7
	_POLY_C = -4.1830e-12
	_PT1000 = 1000
	_SERIES_R = 998.16 		# Adjusted Value (Nominal: 3900 Ohm)

	def __init__(self, boards, period=100):
		self.isoSPI = isoSPI()
		self.sunny_boy = SunnyBoy(period)
		self.boards = boards
		self.blocks = self.boards * BMS._BLOCKS_PER_BOARD
		
		self.balance_cmd = 0
		self.balancing = False
		self.running = False
		self.current = 0
		
		self.ambient_temp_ok = True # True means OK
		self.ambient_temp = 0

		self.cells_not_oh = False # Cells Not Overheated
		self.temp_ok = [False] * self.blocks # True means OK
		
		self.voltages = [0] * self.blocks
		self.cells_not_ov = False # Cells Not Overvoltage (OV)
		self.cell_not_ov = [False] * self.blocks # Individual Cell Not Overvoltage (OV)
		self.cells_not_uv = False # Cells Not Undervoltage (UV)
		self.cell_not_uv = [False] * self.blocks # Individual Cell Not Undervoltage (OV)

	def get_state(self):
		"""Returns the operation state from the battery inverter (Sunny Boy Storage 2.5).
		(Communication to the battery inverter is not actually implemented!)
		"""
		self.running = self.sunny_boy.get_state()

	def get_current_A(self):
		"""Returns the amperage from the battery inverter (Sunny Boy Storage 2.5).
		(Communication to the battery inverter is not actually implemented!)
		"""
		self.current = self.sunny_boy.get_current_A()

	def start(self):
		"""Tells the battery inverter (Sunny Boy Storage 2.5) to start operation.
		(Communication to the battery inverter is not actually implemented!)
		"""
		self.sunny_boy.start()
		self.running = self.get_state()

	def stop(self):
		"""Tells the battery inverter (Sunny Boy Storage 2.5) to stop operation.
		(Communication to the battery inverter is not actually implemented!)
		"""
		self.sunny_boy.stop()
		self.running = self.get_state()

	def polling(self):
		"""Waits until the conversion is complete."""
		completed = False
		while not completed:
			rx = self.isoSPI.xfer(0, 1, BMS._PLADC, [0x0], error_check=False)[0] # Primary Board
			if (rx & 0b1) == 1:
				completed = True

	def rx(self, cmd):
		"""Returns the valid content of a register (in a list).
		Retries as long as the checksum is wrong or the communication fails. Literally forever."""
		while True:
			rx = self.isoSPI.rx(self.boards, cmd)
			if rx is not None:
				return rx

	def tx(self, cmd, data=[]):
		"""Transmits a command and additional data if required.

		Formal parameters:
		cmd -- int
		data -- [int]*self.boards
		"""
		self.isoSPI.tx(0, self.boards, cmd, data) # No return implemented

	def spi(self, bytes_, boards, balance_cmd, balance_data=0, parity=False, crc=False):
		"""Performs an SPI transaction between the LTC6813-1 and the LTC3300-1."""
		# cmd is one of the bytes_
		cmd = BMS._WRCOMM
		if bytes_ == 1:
			balance_data |= 0xffff
			crc = False # Makes sure crc is False (sending a valid checksum is pointless here)
			FCOM0 = BMS._CSBM_High
			ICOM1 = BMS._STOP_Trans
			FCOM1 = BMS._CSBM_High
			ICOM2 = BMS._CSBM_High
		elif bytes_ == 3:
			FCOM0 = BMS._CSBM_Low
			ICOM1 = BMS._CSBM_Low
			FCOM1 = BMS._CSBM_Low
			ICOM2 = BMS._CSBM_Low
		else:
			return None
		payload = [balance_cmd, balance_data]
		ICOM = [BMS._CSBM_Low, ICOM1, ICOM2] # Always start with _CSBM_Low
		FCOM = [FCOM0, FCOM1, BMS._CSBM_High] # Always stop with _CSBM_High
		self.isoSPI.spi(bytes_, boards, cmd, payload, parity, crc, ICOM, FCOM) # No return implemented

	def write_balance_cmd(self, balance_data):
		"""Transmits the given balancing command."""
		# balance_data: int
		balance_cmd = BMS._ADDR | BMS._WBC
		self.spi(3, self.boards, balance_cmd, balance_data, parity=True, crc=True)

	def start_balancing(self):
		"""Starts or renews the balancing."""
		balance_cmd = BMS._ADDR | BMS._EBC
		self.spi(1, self.boards, balance_cmd, parity=True)

	def pause_balancing(self):
		"""Pauses the balancing."""
		balance_cmd = BMS._ADDR | BMS._EBC
		self.spi(1, self.boards, balance_cmd)

	def det_balancing_cmd(self):
		"""Determines the necessary balancing command."""
		average = 0
		for voltage in self.voltages:
			average += voltage
		average /= len(self.voltages)

		threshold = 0.2
		over = []
		under = []
		inside = []
		number_of_over = 0
		number_of_under = 0
		for i, voltage in enumerate(self.voltages):
			if voltage > average + threshold/2:
				over.append(i)
				number_of_over += 1
			elif voltage < average - threshold/2:
				under.append(i)
				number_of_under += 1
			else:
				inside.append(i)

		if number_of_over == number_of_under:
			if number_of_over == 0:
				self.balance_cmd = 0
				return
			over_action = BMS._DCnS
			under_action = BMS._CCn
			inside_action = BMS._DBCn
		elif number_of_over == 0:
			over_action = BMS._DBCn
			under_action = BMS._CCn
			inside_action = BMS._DCnS
		elif number_of_under == 0:
			over_action = BMS._DCnS
			under_action = BMS._DBCn
			inside_action = BMS._CCn
		else:
			over_action = BMS._DCnS
			under_action = BMS._CCn
			inside_action = BMS._DBCn

		balance_cmd = 0
		for cell in over:
			balance_cmd += over_action << (5-cell) * 2
		for cell in under:
			balance_cmd += under_action << (5-cell) * 2
		for cell in inside:
			balance_cmd += inside_action << (5-cell) * 2

		self.balance_cmd = balance_cmd

	def measure_voltages(self):
		"""Measures (only) the voltages from the primary board."""
		if self.balancing:
			self.pause_balancing()
		self.tx(BMS._ADCV | BMS._MD_Normal_3k | BMS._DCP_NP | BMS._CH_All) # Start measurements
		self.polling() # Wait until measurements are finished
		if self.balancing:
			self.start_balancing() # Resume balancing
		cvar_p = self.rx(BMS._RDCVA)[0] # Primary Board
		cvbr_p = self.rx(BMS._RDCVB)[0] # Primary Board
		voltages = self.calc_voltages_from_reg(cvar_p)
		voltages.extend(self.calc_voltages_from_reg(cvbr_p))
		self.voltages = voltages
		self.check_voltages()

	def check_voltages(self):
		"""Checks the voltages for overvoltage and undervoltage."""
		cell_not_ov = []
		cell_not_uv = []
		cells_not_ov = True
		cells_not_uv = True
		for voltage in self.voltages:
			if voltage > 4.2:
				cell_not_ov.append(False)
				cells_not_ov = False
			elif voltage < 2.8:
				cell_not_uv.append(False)
				cells_not_uv = False
			else:
				cell_not_ov.append(True)
				cell_not_uv.append(True)

		self.cell_not_ov = cell_not_ov
		self.cell_not_uv = cell_not_uv
		self.cells_not_ov = cells_not_ov
		self.cells_not_uv = cells_not_uv

	def calc_voltages_from_reg(self, data):
		"""Calculates the voltages from the contents of a register."""
		voltages = []
		for i in range(2, -1, -1):
			low_mask = 0xff << (i*2 + 1) * 8
			high_mask = low_mask >> 8
			low = (data & low_mask) >> (i*2 + 1) * 8
			high = (data & high_mask) >> i*16
			high <<= 8
			voltages.append((high + low) * 100e-6)
		return voltages

	def temp_mon(self):
		"""Checks if the temperature of each cell (6 blocks à 36 cells) is OK."""
		temp_ok = []
		cells_not_oh = True
		for i in range(self.blocks):
			data = [i << 5*8] * self.boards
			self.tx(BMS._WRCFGB, data)
			cfgar_p = self.rx(BMS._RDCFGA)[0] # Primary Board
			logic_level = cfgar_p & (0b1 << (5*8 + 4)) # Active-High Signal
			if logic_level:
				temp_ok.append(False)
				cells_not_oh = False
			else:
				temp_ok.append(True)

		self.temp_ok = temp_ok
		self.cells_not_oh = cells_not_oh

	def measure_ambient_temp(self):
		"""Measures the ambient temperature."""
		self.tx(BMS._ADAX | BMS._MD_Normal_3k | BMS._CHG_All)
		self.polling()
		avbr_p = self.rx(BMS._RDAUXB)[0] # Primary Board
		avar_p = self.rx(BMS._RDAUXA)[0] # Primary Board
		v_ref2 = self.calc_voltages_from_reg(avbr_p)[2]
		v_pt1000 = self.calc_voltages_from_reg(avar_p)[0]
		if v_ref2 <= v_pt1000 or v_pt1000 == 0:
			self.ambient_temp = -274
		else:
			rt = BMS._SERIES_R / (v_ref2/v_pt1000 - 1)
			self.ambient_temp = self.temp(BMS._PT1000, rt)
		if self.ambient_temp >= 0 and self.ambient_temp <= 45:
			self.ambient_temp_ok = True
		else:
			self.ambient_temp_ok = False

	def temp(self, r0, rt):
		"""Calculates the temperature from r0 and rt."""
		num = r0 * BMS._POLY_A
		disc = r0**2 * BMS._POLY_A**2 - 4 * r0 * BMS._POLY_B * (r0 - rt)
		den = 2 * r0 * BMS._POLY_B
		return (-num + sqrt(disc)) / den

def main():
	pass

if __name__ == "__main__":
	main()
