import csv
import concurrent.futures
import pandas as pd
import queue
from filters_lib import filters_sdk, filter_types
from neurosdk.scanner import Scanner
from neurosdk.cmn_types import *
from time import sleep

"""
Filter setup

Luxembourg's power grit has a frequency of 50Hz so we exclude it here.

High and low pass based on Brainbit's recommendations. 
A heealthy human eeg frequency range is 1 - 30-70Hz.

Source: https://sdk.brainbit.com/device-recommendation/
Source: https://en.wikipedia.org/wiki/Electroencephalography
"""
FILTER_LIST = filters_sdk.FilterList()
SAMPLING_FREQUENCY = 250
EXCLUDE_FREQUENCY = 50 
HIGH_PASS_FREQUENCY = 1
LOW_PASS_FREQUENCY = 30

DATA_QUEUE = queue.Queue()
OUTPUT_FILE = 'data/data_filtered.csv'
    
def sensor_found(scanner, sensors):
    for index in range(len(sensors)):
        print('... sensor found: %s' % sensors[index])
 
def on_sensor_state_changed(sensor, state):
    print('... sensor {0} is {1}'.format(sensor.name, state))
 
def on_battery_changed(sensor, battery):
    print('... battery: {0}'.format(battery))
 
def save_filtered_data_to_csv(filtered_O1, filtered_O2, filtered_T3, filtered_T4):
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([filtered_O1, filtered_O2, filtered_T3, filtered_T4])
  
def on_signal_received(sensor, data):
    for packet in data:
        DATA_QUEUE.put(packet)
        filtered_O1 = FILTER_LIST.filter(packet.O1)
        filtered_O2 = FILTER_LIST.filter(packet.O2)
        filtered_T3 = FILTER_LIST.filter(packet.T3)
        filtered_T4 = FILTER_LIST.filter(packet.T4)
        save_filtered_data_to_csv(filtered_O1, filtered_O2, filtered_T3, filtered_T4)

def collect_filtered_data():
    f1 = filters_sdk.Filter()
    f1.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_band_stop, SAMPLING_FREQUENCY, EXCLUDE_FREQUENCY))
    
    f2 = filters_sdk.Filter()
    f2.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_lp, SAMPLING_FREQUENCY, LOW_PASS_FREQUENCY))
    
    f3 = filters_sdk.Filter()
    f3.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_hp, SAMPLING_FREQUENCY, HIGH_PASS_FREQUENCY))
    
    FILTER_LIST.add_filter(f1)
    FILTER_LIST.add_filter(f2)
    FILTER_LIST.add_filter(f3)
    
    try:
        print('collect_filtered_data start')
        scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LEBrainBitBlack])
        scanner.sensorsChanged = sensor_found
        scanner.start()
        print("... starting search for 5 sec")
        sleep(5)
        scanner.stop()
    
        sensorsInfo = scanner.sensors()
        for i in range(len(sensorsInfo)):
            current_sensor_info = sensorsInfo[i]

            def device_connection(sensor_info):
                return scanner.create_sensor(sensor_info)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(device_connection, current_sensor_info)
                sensor = future.result()
                print("... device connected")

            sensor.sensorStateChanged = on_sensor_state_changed
            sensor.batteryChanged = on_battery_changed

            if sensor.is_supported_feature(SensorFeature.Signal):
                sensor.signalDataReceived = on_signal_received
                sensor.exec_command(SensorCommand.StartSignal)
                print("... start signal for 5 seconds")
                sleep(5)
                sensor.exec_command(SensorCommand.StopSignal)
                print("... stop signal")

            sensor.disconnect()
            print("... disconnect from sensor")
            del sensor

        del scanner
        print('... remove scanner')
        print('collect_filtered_data end')

    except Exception as err:
        print(err)
