#!/usr/bin/env python3

"""theBMS ~ Safe, Easy and Affordable
Copyright © 2019 pro3E - Team4
"""

from classes.BMS import BMS

def renew_balancing(bms):
	if bms.balancing:
		bms.start_balancing()

def main():
	bms = BMS(1, period=100)

	while True:
		bms.measure_ambient_temp()
		renew_balancing(bms)
		bms.temp_mon()
		renew_balancing(bms)
		bms.measure_voltages()

		# Debug
		print("#####################")
		print("ambient_temp_ok: " + str(bms.ambient_temp_ok))
		print("ambient_temp: " + str(bms.ambient_temp))
		print("cells_not_oh: " + str(bms.cells_not_oh))
		print("temp_ok: " + str(bms.temp_ok))
		print("voltages: " + str(bms.voltages))
		print("cells_not_ov: " + str(bms.cells_not_ov))
		print("cell_not_ov: " + str(bms.cell_not_ov))
		print("cells_not_uv: " + str(bms.cells_not_uv))
		print("cell_not_uv: " + str(bms.cell_not_uv))
		# Debug

		balancing = bms.ambient_temp_ok and bms.cells_not_oh and bms.cells_not_ov and bms.cells_not_uv
		# *** Implement check for the state (running or stopped) ***
		if balancing:
			bms.det_balancing_cmd()
			bms.write_balance_cmd(bms.balance_cmd)
			bms.start_balancing()
			bms.balancing = True
			bms.get_state()
			if not bms.running:
				bms.start()
		else:
			bms.pause_balancing()
			bms.balancing = False
			bms.get_state()
			if bms.running:
				bms.stop()

if __name__ == "__main__":
	main()
