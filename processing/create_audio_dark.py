import csv
import subprocess
from collections import deque
from midiutil import MIDIFile
from pydub import AudioSegment
 
# MIDI Note Constants
C7_NOTE = 96
C1_NOTE = 24
BASE_TEMPO = 120
DURATION_BASE = 0.5
 
SCALE = [57, 60, 62, 64, 67, 69, 72, 74]
EXTENDED_SCALE = [
    note + 12 * octave
    for octave in range(-10, 11)
    for note in SCALE
    if 0 <= note + 12 * octave <= 127
]

SF2_FILE = "tools/FluidR3_GM/FluidR3_GM.sf2"
WAV_FILE = "artifacts/audio-dark.wav"
MP3_FILE = "artifacts/audio-dark.mp3"
 
def adjust_high_pitch(pitch):
    return pitch - 48 if pitch > C7_NOTE else pitch
 
def quantize_to_scale(pitch):
    return min(EXTENDED_SCALE, key=lambda x: abs(x - pitch))
 
def normalize_data(data_list, min_val=0, max_val=127):
    data_min, data_max = min(data_list), max(data_list)
    if data_max == data_min:
        return [int((min_val + max_val) / 2)] * len(data_list)
    return [
        int((value - data_min) / (data_max - data_min) * (max_val - min_val) + min_val)
        for value in data_list
    ]
 
def create_midi(input_file, output_file):
    print("Creating modular-inspired MIDI...")
 
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
 
        max_samples = 500
        channels = ['O1', 'O2', 'T3', 'T4']
        channel_data = {ch: deque(maxlen=max_samples) for ch in channels}
 
        for row in reader:
            if len(row) == len(channels):
                for i, channel in enumerate(channels):
                    channel_data[channel].append(float(row[i]))
 
    pitches = normalize_data(channel_data['O1'])
    velocities = normalize_data(channel_data['O2'])
 
    midi_file = MIDIFile(1)
    track, channel, time = 0, 0, 0
 
    midi_file.addTempo(track, time, BASE_TEMPO)
 
    last_low_note = None
    note_active = False
 
    for i, raw_pitch in enumerate(pitches):
        pitch = adjust_high_pitch(raw_pitch)
        pitch = quantize_to_scale(pitch)
 
       
        note_duration = DURATION_BASE + (channel_data['T4'][i] * 0.1)
        velocity = velocities[i]
 
        if pitch < C1_NOTE:
            # Start or change low note
            if pitch != last_low_note:
                last_low_note = pitch
                midi_file.addNote(track, channel, pitch, time + i * DURATION_BASE, note_duration, velocity)
                note_active = True
            else:
                # Sustain current low note
                midi_file.addNote(track, channel, last_low_note, time + i * DURATION_BASE, note_duration, velocity)
        elif last_low_note and note_active:
            # Sustain previous low note when current note is above C1
            midi_file.addNote(track, channel, last_low_note, time + i * DURATION_BASE, note_duration, velocity)
 
    with open(output_file, "wb") as file:
        midi_file.writeFile(file)
 
    print(f"MIDI file saved: {output_file}")

def convert_midi_to_mp3(midi_file, soundfont_path, wav_output, mp3_output):
    # Step 1: Convert MIDI to WAV using the fluidsynth CLI
    subprocess.run([
        "fluidsynth",
        "-ni", soundfont_path,
        midi_file,
        "-F", wav_output,
        "-r", "44100"
    ], check=True)

    # Step 2: Convert WAV to MP3
    audio = AudioSegment.from_wav(wav_output)
    audio.export(mp3_output, format="mp3")
    
    # Remove the temporary files
    subprocess.run(["rm", wav_output], check=True)
    subprocess.run(["rm", midi_file], check=True)

    print(f"✅ Done! MP3 saved to: {mp3_output}")

def create_audio(input_file, output_file):
    create_midi(input_file, output_file)
    convert_midi_to_mp3(output_file, SF2_FILE, WAV_FILE, MP3_FILE)