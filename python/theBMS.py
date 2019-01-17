#!/usr/bin/env python3

"""theBMS ~ Safe, Easy and Affordable
Copyright © 2019 pro3E - Team4
"""

from multiprocessing import Process
from classes.BMS import BMS
from time import time
import _mysql

def renew_balancing(bms):
	if bms.balancing:
		bms.start_balancing()

def push_to_db(query):
	host = "hostname"
	port = 3306
	user = "username"
	passwd = "password"
	db = "database"

	try:
		db = _mysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
		db.query(query)
		db.close()
	except:
		pass

def main():
	bms = BMS(1, period=100)
	counter = 2

	while True:
		renew_balancing(bms)
		bms.measure_ambient_temp()
		renew_balancing(bms)
		bms.temp_mon()
		renew_balancing(bms)
		if counter == 2:
			bms.measure_voltages()
			renew_balancing(bms)
			counter = 0
		else:
			counter += 1

		# Debug -------------------------------------
		# print("##################################")
		# print("ambient_temp_ok: " + str(bms.ambient_temp_ok))
		# print("ambient_temp: " + str(bms.ambient_temp))
		# print("cells_not_oh: " + str(bms.cells_not_oh))
		# print("temp_ok: " + str(bms.temp_ok))
		# print("voltages: " + str(bms.voltages))
		# print("cells_not_ov: " + str(bms.cells_not_ov))
		# print("cell_not_ov: " + str(bms.cell_not_ov))
		# print("cells_not_uv: " + str(bms.cells_not_uv))
		# print("cell_not_uv: " + str(bms.cell_not_uv))
		# Debug -------------------------------------

		balancing = bms.ambient_temp_ok and bms.cells_not_oh and bms.cells_not_ov and bms.cells_not_uv
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

		# Compute Query Command
		query = "UPDATE bms SET timestamp = '" + str(int(time()))
		query += "', balancing = '" + str(int(bms.balancing))
		query += "', temp = '{:.1f}".format(bms.ambient_temp)
		query += "', v1 = '{:.3f}".format(bms.voltages[0])
		query += "', v2 = '{:.3f}".format(bms.voltages[1])
		query += "', v3 = '{:.3f}".format(bms.voltages[2])
		query += "', v4 = '{:.3f}".format(bms.voltages[3])
		query += "', v5 = '{:.3f}".format(bms.voltages[4])
		query += "', v6 = '{:.3f}".format(bms.voltages[5])
		query += "', m1 = '" + str(int(bms.temp_ok[0]))
		query += "', m2 = '" + str(int(bms.temp_ok[1]))
		query += "', m3 = '" + str(int(bms.temp_ok[2]))
		query += "', m4 = '" + str(int(bms.temp_ok[3]))
		query += "', m5 = '" + str(int(bms.temp_ok[4]))
		query += "', m6 = '" + str(int(bms.temp_ok[5]))
		query += "', balancecmd = '" + str(bms.balance_cmd)
		query += "' WHERE id = '0'"

		p = Process(target=push_to_db, args=[query])
		p.start()

if __name__ == "__main__":
	main()
