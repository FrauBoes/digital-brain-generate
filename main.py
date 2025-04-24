import eeg.collect_filtered_data
# import eeg.interpolate_data
import nfc_tag.read_uuid
import processing.create_audio
import processing.create_audio_dark
"""
import processing.create_quadrant_animation
import processing.combine_audio_video
# import processing.create_radar_animation
# import processing.create_radar_animation
"""
import upload.upload_artifacts
# import time

FILE_DATA_FILTERED = 'data/data_filtered.csv'
"""
FILE_DATA_INTERPOLATED = 'data/data_interpolated.csv'
FILE_RADAR_ANIMATION = 'artifacts/radar_animation.mp4'
FILE_QUADRANT_ANIMATION = 'artifacts/quadrant_animation.mp4'
"""
FILE_AUDIO = 'artifacts/audio.mid'
FILE_AUDIO_NEW = 'artifacts/audio-dark.mid'
FILE_AUDIO_MP3 = 'artifacts/audio-happy.mp3'
FILE_AUDIO_VIDEO = 'artifacts/audio_video.mp4'

# Read uuid
uuid = nfc_tag.read_uuid.read_uuid()

# Read and preprocess data
eeg.collect_filtered_data.collect_filtered_data()
# eeg.interpolate_data.interpolate_to_16_columns(FILE_DATA_FILTERED, FILE_DATA_INTERPOLATED)

# Create artifacts
# processing.create_radar_animation.run_radar_animation(FILE_DATA_INTERPOLATED, FILE_RADAR_ANIMATION)
# processing.create_quadrant_animation.run_quadrant_animation(FILE_DATA_INTERPOLATED, FILE_QUADRANT_ANIMATION)
processing.create_audio.create_audio(FILE_DATA_FILTERED,FILE_AUDIO)
processing.create_audio_dark.create_audio(FILE_DATA_FILTERED, FILE_AUDIO_NEW)
# processing.combine_audio_video.combine_audio_to_video(FILE_QUADRANT_ANIMATION, FILE_AUDIO_MP3, FILE_AUDIO_VIDEO)

# Upload artifacts
upload.upload_artifacts.upload_artifacts(uuid)