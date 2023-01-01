from pymodbus.constants import Defaults
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import subprocess
import json
import time
import pdb
import os

scheduling_seconds = 10.0

inverter_host = "192.168.200.1"
inverter_port = 6607
inverter_id = 0

inverter_sensors = [
  ["inverter_status_1", "uint16", 0, 1, 0, "Inverter Status 1", 0],
  ["inverter_status_2", "uint16", 2, 1, 0, "Inverter Status 2", 0],
  ["inverter_status_3", "uint32", 3, 2, 0, "Inverter Status 3", 0],
  ["inverter_alarm_1", "uint16", 8, 1, 0, "Inverter Alarm 1", 0],
  ["inverter_alarm_2", "uint16", 9, 1, 0, "Inverter Alarm 2", 0],
  ["inverter_alarm_3", "uint16", 10, 1, 0, "Inverter Alarm 3", 0],
  ["inverter_string_1_v", "int16", 16, 1, 0.1, "Inverter String 1 DC Voltage (V)", 0],
  ["inverter_string_1_a", "int16", 17, 1, 0.01, "Inverter String 1 DC Current (A)", 0],
  ["inverter_dc_p", "int32", 64, 2, 0.001, "Inverter DC Power (kW)", 0],
  ["inverter_ac_v", "uint16", 66, 1, 0.1, "Inverter AC Voltage (V)", 0],
  ["inverter_ac_a", "int32", 72, 2, 0.001, "Inverter AC Current (A)", 0],
  ["inverter_ac_p", "int32", 80, 2, 0.001, "Inverter AC Power (kW)", 0],
  ["inverter_pf", "int16", 84, 1, 0.001, "Inverter Power Factor", 0],
  ["inverter_f", "uint16", 85, 1, 0.01, "Inverter Frequency (Hz)", 0],
  ["inverter_efficiency", "uint16", 86, 1, 0.01, "Inverter Efficiency (%)", 0],
  ["inverter_temp", "int16", 87, 1, 0.1, "Inverter Temperature (C)", 0],
  ["inverter_insulation_r", "uint16", 88, 1, 0.001, "Inverter Insulation Resistency (Mohms)", 0],
  ["inverter_device_status", "uint16", 89, 1, 1, "Inverter Device Status", 0]
]

meter_sensors = [
  ["meter_status", "uint16", 0, 1, 1, "Meter Status", 0],
  ["meter_v", "int32", 1, 2, 0.1, "Meter Voltage (V)", 0],
  ["meter_a", "int32", 7, 2, 0.01, "Meter Current (A)", 0],
  ["meter_p", "int32", 13, 2, 1, "Meter Active Power (W)", 0],
  ["meter_reactive_p", "int32", 15, 2, 1, "Meter Reactive Power (Var)", 0],
  ["meter_pf", "int16", 17, 1, 0.001, "Meter Power Factor", 0],
  ["meter_f", "int16", 18, 1, 0.01, "Meter Frequency (Hz)", 0],
  ["meter_positive_power", "int32", 19, 2, 0.01, "Meter Exported Power (kWh)", 0],
  ["meter_reverse_power", "int32", 21, 2, 0.01, "Meter Imported Power (kWh)", 0]
]


def decode_data(decoder, type, size):
  if type == "int16":
    return decoder.decode_16bit_int()
  elif type == "uint16":
    return decoder.decode_16bit_uint()
  elif type == "int32":
    return decoder.decode_32bit_int()
  elif type == "uint32":
    return decoder.decode_32bit_uint()
  else:
    print("Unsupported data type: " + type)
    return 0


def recover_all_sensors(sensors, registers):
  for sensor in sensors:
    data_registers = registers[sensor[2]:sensor[2]+sensor[3]]
    decoder = BinaryPayloadDecoder.fromRegisters(data_registers, byteorder=Endian.Big)
    data = decode_data(decoder, sensor[1], sensor[3])
    if sensor[4] != 0:
       data = data * sensor[4]
    if type(data) is float:
      data_hex = ""
    else:
      data_hex = " [" + hex(data) + "]"
    sensor[6] = data
    print(sensor[5] + ": " + str(data) + data_hex)

start_time = time.time()
i = 0

while True:
    print(">>>> Iteration " + str(i))
    i = i + 1

    client = ModbusTcpClient(host=inverter_host, port=inverter_port, unit_id=inverter_id)
    client.connect()

    if client.connect():
      print(">> Connected to: " + inverter_host + ":" + str(inverter_port))
      time.sleep(2)

      inverter_data = client.read_holding_registers(32000, 90)
      meter_data = client.read_holding_registers(37100, 23)

      recover_all_sensors(inverter_sensors, inverter_data.registers)
      recover_all_sensors(meter_sensors, meter_data.registers)

      client.close()
      print(">> Connection closed: " + inverter_host + ":" + str(inverter_port))

    time.sleep(scheduling_seconds - ((time.time() - start_time) % scheduling_seconds))
