from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

scheduling_seconds = 6.0

inverter_host = "192.168.200.1"
inverter_port = 6607
inverter_id = 0

modbus_wait_for_connnection = 2.0

influx_url = "http://192.168.1.95:8086"
influx_token = "nHFF0UL3kgcjWEvUjvxeUrjS7DfJFzdohW22o0VaYGSs2SH6wvbQAMJXO1uf6TgH9BDS0N-gLJ45lvYbjbd2HA=="
influx_org = "sun2000"
influx_measurement = "sun2000"
influx_measurement_version = "1.0"
influx_bucket = "sensors"

inverter_starting_address = 32000
inverter_register_count = 116
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
  ["inverter_ac_p_peak", "int32", 78, 2, 0.001, "Inverter AC Power Peak (kW)", 0],
  ["inverter_ac_p", "int32", 80, 2, 0.001, "Inverter AC Power (kW)", 0],
  ["inverter_ac_reactive_p", "int32", 82, 2, 0.001, "Inverter AC Reactive Power (kVar)", 0],
  ["inverter_pf", "int16", 84, 1, 0.001, "Inverter Power Factor", 0],
  ["inverter_f", "uint16", 85, 1, 0.01, "Inverter Frequency (Hz)", 0],
  ["inverter_efficiency", "uint16", 86, 1, 0.01, "Inverter Efficiency (%)", 0],
  ["inverter_temp", "int16", 87, 1, 0.1, "Inverter Temperature (C)", 0],
  ["inverter_insulation_r", "uint16", 88, 1, 0.001, "Inverter Insulation Resistency (Mohms)", 0],
  ["inverter_device_status", "uint16", 89, 1, 1, "Inverter Device Status", 0],
  ["inverter_accumulated_p", "uint32", 106, 2, 0.01, "Inverter Accumulated energy yield", 0],
  ["inverter_daily_p", "uint32", 114, 2, 0.01, "Inverter Daily energy yield", 0]
]

meter_starting_address = 37100
meter_register_count = 23
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


def store_all_sensors(sensors, points):
  for sensor in sensors:
    p = Point(influx_measurement).tag("version", influx_measurement_version).field(sensor[0], sensor[6])
    points.append(p)


def gather_modbus_data():
  modbus_client = ModbusTcpClient(host=inverter_host, port=inverter_port, unit_id=inverter_id)

  if modbus_client.connect():
    print(">> MODBUS connected to: " + inverter_host + ":" + str(inverter_port))
    time.sleep(modbus_wait_for_connnection)

    inverter_data = modbus_client.read_holding_registers(inverter_starting_address, inverter_register_count)
    meter_data = modbus_client.read_holding_registers(meter_starting_address, meter_register_count)

    recover_all_sensors(inverter_sensors, inverter_data.registers)
    recover_all_sensors(meter_sensors, meter_data.registers)

    modbus_client.close()
    print(">> MODBUS connection closed: " + inverter_host + ":" + str(inverter_port))

    return True
  else:
    return False


def store_influx_data():
  influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
  
  if influx_client.ready():
    print(">> Influx connected to: " + influx_url)

    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    points = []

    store_all_sensors(inverter_sensors, points)
    store_all_sensors(meter_sensors, points)

    write_api.write(bucket=influx_bucket, record=points)

    influx_client.close()
    print(">> Influx connection closed: " + influx_url)


def main():

  start_time = time.time()
  i = 0

  while True:
    print(">>>> Iteration " + str(i)) 

    if gather_modbus_data():
      store_influx_data()    

    time.sleep(scheduling_seconds - ((time.time() - start_time) % scheduling_seconds))
    i = i + 1


if __name__ == "__main__":
  main()