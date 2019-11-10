#!/usr/bin/python3
import time
from pysystemair_save_vtr import SystemairSaveVTR
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient

client = ModbusClient(host='192.168.0.111')
client.connect()
unit = SystemairSaveVTR(client, 1)
unit.update()

print("User mode: " + str(unit.get_user_mode))
print("Supply temp: " + str(unit.get_supply_temp))
print("Extract temp: " + str(unit.get_extract_temp))
print("Setpoint temp: " + str(unit.get_setpoint_temp))
print("Outdoor temp: " + str(unit.get_outdoor_temp))
print("Cooler: " + str(unit.get_cooler))
print("Cooler state: " + str(unit.get_cooler_state))
print("Heater: " + str(unit.get_heater))
print("Heater state: " + str(unit.get_heater_state))
print("Heat ex: " + str(unit.get_heat_exchanger))
print("Heat ex state: " + str(unit.get_heat_exchanger_state))
print("Filter warning: " + str(unit.get_filter_warning))
print("Filter time: " + str(unit.get_filter_remaining_hours))
print("Fan speed supply: " + str(unit.get_fan_speed_supply))
print("REG_SENSOR_OAT: " + str(unit.get_raw_input_register('REG_SENSOR_OAT')))

#print("Setting supply fan to 2")
#unit.set_fan_speed_supply(2)
#time.sleep(3)
#unit.update()
#print("Fan speed supply: " + str(unit.get_fan_speed_supply))

#print("Setting supply fan to 3")
#unit.set_fan_speed_supply(3)
#time.sleep(3)
#unit.update()
#print("Fan speed supply: " + str(unit.get_fan_speed_supply))

client.close()
