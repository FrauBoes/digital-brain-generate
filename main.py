import eeg.collect_filtered_data
import eeg.interpolate_data
import time

FILE_DATA_FILTERED = 'data/data-filtered.csv'
FILE_DATA_INTERPOLATED = 'data/data-interpolated.csv'

eeg.collect_filtered_data.collect_filtered_data()
time.sleep(30)
eeg.interpolate_data.interpolate_to_16_columns(FILE_DATA_FILTERED, FILE_DATA_INTERPOLATED)
