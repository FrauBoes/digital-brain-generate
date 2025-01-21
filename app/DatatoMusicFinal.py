from midiutil import MIDIFile
import csv
from collections import deque

# Open the CSV file for reading
csv_file = open('CollectedDataFiltered.csv', mode='r')
reader = csv.reader(csv_file)

# Skip the header if there is one
next(reader, None)

# Set the desired number of samples
max_samples = 500
channels = ['O1', 'O2', 'T3', 'T4']

# Initialize the dictionary with deques for each channel
channel_data = {channel: deque(maxlen=max_samples) for channel in channels}

# Iterate over the rows in the CSV file
for row in reader:
    if len(row) == len(channels):
        for i, channel in enumerate(channels):
            channel_data[channel].append(float(row[i]))

csv_file.close()

# Normalize data for MIDI notes (0-127)
def normalize_data_to_notes(channel_data):
    """Normalize data to fit MIDI note range (0–127)."""
    data_min = min(channel_data['O1'])
    data_max = max(channel_data['O1'])
    return [
        int((value - data_min) / (data_max - data_min) * 127)
        for value in channel_data['O1']
    ]

# Normalize data for velocity (0-127)
def normalize_data_to_velocities(channel_data):
    """Normalize a list of data to fit within MIDI velocity range."""
    data_min = min(channel_data['O2'])
    data_max = max(channel_data['O2'])
    return [
        int((value - data_min) / (data_max - data_min) * 127)
        for value in channel_data['O2']
    ]

# Normalize data to MIDI notes and velocity range 
pitches = normalize_data_to_notes(channel_data)
velocities = normalize_data_to_velocities(channel_data)

# Parameters for MIDI generation
tempo = 120  # Initial tempo
duration = 0.5  # Fixed duration for each note
channel = 0
time = 0

# Define the threshold for shifting notes above "G7" (MIDI note 103)
G7_NOTE = 103  # MIDI note number for G7

# Function to shift notes above G7 down by four octaves (48 semitones)
def adjust_high_pitch(pitch):
    """Shift pitches above G7 (MIDI note 103) down by four octaves (48 semitones)."""
    if pitch > G7_NOTE:
        pitch -= 48  # Shift down by four octaves (48 semitones)
    return pitch

# Initialize MIDI file
midi_file = MIDIFile(1)  # One track
track = 0

# Set initial tempo
midi_file.addTempo(track, time, tempo)

# Add notes with dynamic tempo adjustments based on T3 and T4
for i, (pitch, velocity) in enumerate(zip(pitches, velocities)):
    # Adjust pitch if it is above G7 (MIDI note 103)
    pitch = adjust_high_pitch(pitch)

    # Modify tempo based on T3 (could be a more complex function)
    dynamic_tempo = tempo + int(channel_data['T3'][i] * 10)  # Small tempo change based on T3
    midi_file.addTempo(track, time + i * duration, dynamic_tempo)

    # Modify note duration based on T4 (rhythm variation)
    note_duration = duration + (channel_data['T4'][i] * 0.1)  # Small variation in note duration

    # Add the note to the track
    midi_file.addNote(track, channel, pitch, time + i * duration, note_duration, velocity)

# Write MIDI file to disk
output_file = "data-driven-music_with_shifted_pitches_v3.mid"
with open(output_file, "wb") as file:
    midi_file.writeFile(file)

print(f"MIDI file generated: {output_file}")
