from neurosdk.scanner import Scanner
from neurosdk.cmn_types import *
from filters_lib import filters_sdk, filter_types
import os
import queue
import csv

import concurrent.futures
from time import sleep

flist = filters_sdk.FilterList()
data_queue = queue.Queue()

def sensor_found(scanner, sensors):
    for index in range(len(sensors)):
        print('Sensor found: %s' % sensors[index])


def on_sensor_state_changed(sensor, state):
    print('Sensor {0} is {1}'.format(sensor.name, state))


def on_battery_changed(sensor, battery):
    print('Battery: {0}'.format(battery))


## Function to save data to CSV
def save_filtered_data_to_csv(filtered_O1,filtered_O2,filtered_T3,filtered_T4):
    ##Storing to an existing file
    # file_exists = os.path.isfile('CollectedData.csv')

    with open('CollectedDataFiltered.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the filtered data to the CSV
        writer.writerow([filtered_O1, filtered_O2, filtered_T3, filtered_T4])

        ###Ways to Store the data
        ##Check if the file is empty or doesn't exist and write the header
        # if file.tell() == 0:  # This checks if the file is empty (or just created)
        # writer.writerow(['O1', 'O2', 'T3', 'T4'])  # Write header if file doesn't exist or is empty
        #if not file_exists:
        #    writer.writerow(['PackNum', 'Marker', 'O1', 'O2', 'T3', 'T4'])  # Write header if file doesn't exist
        #writer.writerow([packet.PackNum, packet.Marker, packet.O1, packet.O2, packet.T3, packet.T4])

        ##To (PackNum, Marker are not stored here):
        # if not file_exists:
        # writer.writerow(['O1', 'O2', 'T3', 'T4'])  # Write header if file doesn't exist
        # writer.writerow([filtered_O1,filtered_O2,filtered_T3,filtered_T4])

# filters setup
f1 = filters_sdk.Filter()
f1.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_band_stop, 250, 60))

f3 = filters_sdk.Filter()
f3.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_lp, 250, 30)) # for EEG

f4 = filters_sdk.Filter()
f4.init_by_param(filter_types.FilterParam(filter_types.FilterType.ft_hp, 250, 4)) # for EEG

flist.add_filter(f1)
flist.add_filter(f3)
flist.add_filter(f4)

## Data Receiving and Printing
# def on_signal_received(sensor, data):
# print(data)

def on_signal_received(sensor, data):
    ##Isolating and storing data in variables in arrays and filtering them
    # samples_o1 = [x.O1 for x in data]
    # samples_o1 = flist.filter_array(samples_o1)
    # print(samples_o1)
    # samples_o2 = [x.O2 for x in data]
    # samples_o2 = flist.filter_array(samples_o2)
    # print(samples_o2)
    # samples_t3 = [x.T3 for x in data]
    # samples_t3 = flist.filter_array(samples_t3)
    # print(samples_t3)
    # samples_t4 = [x.T4 for x in data]
    # samples_t4 = flist.filter_array(samples_t4)
    # print(samples_t4)
    
    #Saving Filtered Data
    for packet in data:
        data_queue.put(packet)
        #print(packet)
        filtered_O1 = flist.filter(packet.O1)
        filtered_O2 = flist.filter(packet.O2)
        filtered_T3 = flist.filter(packet.T3)
        filtered_T4 = flist.filter(packet.T4)
 
        save_filtered_data_to_csv(filtered_O1,filtered_O2,filtered_T3,filtered_T4)

def on_resist_received(sensor, data):
    print(data)

#Motion Related Data
def on_mems_received(sensor, data):
    print(data)

#High-speed data streams for physiological signals
def on_fpg_received(sensor, data):
    print(data)


def on_amp_received(sensor, data):
    print(data)


try:
    #Scans surrounds from sensors. 
    scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LEBrainBitBlack])

    scanner.sensorsChanged = sensor_found
    scanner.start()
    print("Starting search for 5 sec...")
    sleep(5)
    scanner.stop()

    #For each of the connected Devices do
    sensorsInfo = scanner.sensors()
    for i in range(len(sensorsInfo)):
        #Prints Basic Information about the device
        current_sensor_info = sensorsInfo[i]
        print(sensorsInfo[i])
        def device_connection(sensor_info):
            return scanner.create_sensor(sensor_info)

        #Connects with the mentioned device
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(device_connection, current_sensor_info)
            sensor = future.result()
            print("Device connected")

        #Calback function to update Sensor Information
        sensor.sensorStateChanged = on_sensor_state_changed
        sensor.batteryChanged = on_battery_changed

        sensFamily = sensor.sens_family
        sensorState = sensor.state
        if sensorState == SensorState.StateInRange:
            print("connected")
        else:
            print("Disconnected")

        #Prints Basic information about the connected device
        print(sensFamily)
        print(sensor.features)
        print(sensor.commands)
        print(sensor.parameters)
        print(sensor.name)
        print(sensor.state)
        print(sensor.address)
        print(sensor.serial_number)
        print(sensor.batt_power)
        
        #Checking Sensor Parameter Support
        if sensor.is_supported_parameter(SensorParameter.SamplingFrequency):
            print(sensor.sampling_frequency)
        if sensor.is_supported_parameter(SensorParameter.Gain):
            print(sensor.gain)
        if sensor.is_supported_parameter(SensorParameter.Offset):
            print(sensor.data_offset)
        print(sensor.version)

        sensor.sensorAmpModeChanged = on_amp_received

        if sensor.is_supported_feature(SensorFeature.Signal):
            sensor.signalDataReceived = on_signal_received

        if sensor.is_supported_feature(SensorFeature.Resist):
            sensor.resistDataReceived = on_resist_received

        if sensor.is_supported_feature(SensorFeature.MEMS):
            sensor.memsDataReceived = on_mems_received

        if sensor.is_supported_feature(SensorFeature.FPG):
            sensor.fpgDataReceived = on_fpg_received

        if sensor.is_supported_command(SensorCommand.StartSignal):
            sensor.exec_command(SensorCommand.StartSignal)
            print("Start signal")
            sleep(5)
            sensor.exec_command(SensorCommand.StopSignal)
            print("Stop signal")

        if sensor.is_supported_command(SensorCommand.StartFPG):
            sensor.exec_command(SensorCommand.StartFPG)
            print("Start FPG")
            sleep(5)
            sensor.exec_command(SensorCommand.StopFPG)
            print("Stop FPG")

        if sensor.is_supported_command(SensorCommand.StartResist):
            sensor.exec_command(SensorCommand.StartResist)
            print("Start resist")
            sleep(5)
            sensor.exec_command(SensorCommand.StopResist)
            print("Stop resist")

        if sensor.is_supported_command(SensorCommand.StartMEMS):
            sensor.exec_command(SensorCommand.StartMEMS)
            print("Start MEMS")
            sleep(5)
            sensor.exec_command(SensorCommand.StopMEMS)
            print("Stop MEMS")

        sensor.disconnect()
        print("Disconnect from sensor")
        del sensor

    del scanner
    print('Remove scanner')
except Exception as err:
    print(err)
