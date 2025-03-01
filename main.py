import eeg.collect_filtered_data
import eeg.interpolate_data
import nfc_tag.read_uuid_from_nfc_tag
import processing.create_audio
import processing.create_quadrant_animation
import processing.create_radar_animation
import processing.create_radar_animation
import upload.upload_artifacts
import time

FILE_DATA_FILTERED = 'data/data_filtered.csv'
FILE_DATA_INTERPOLATED = 'data/data_interpolated.csv'
FILE_RADAR_ANIMATION = 'artifacts/radar_animation.mp4'
FILE_QUADRANT_ANIMATION = 'artifacts/quadrant_animation.mp4'
FILE_AUDIO = 'artifacts/audio.mid'

# Read and preprocess data
eeg.collect_filtered_data.collect_filtered_data()
time.sleep(30)
eeg.interpolate_data.interpolate_to_16_columns(FILE_DATA_FILTERED, FILE_DATA_INTERPOLATED)

# Create artifacts
processing.create_radar_animation.run_radar_animation(FILE_DATA_INTERPOLATED, FILE_RADAR_ANIMATION)
processing.create_quadrant_animation.run_quadrant_animation(FILE_DATA_INTERPOLATED, FILE_QUADRANT_ANIMATION)
processing.create_audio.create_audio(FILE_DATA_FILTERED,FILE_AUDIO)

# Read uuid
uuid = nfc_tag.read_uuid_from_nfc_tag.get_uuid()

# Upload artifacts
# for testing
# uuid = '8e980119-44e2-4e9c-9a90-879f6e05ceee'
upload.upload_artifacts.upload_artifacts(uuid)