import csv
import numpy as np
import platform
import subprocess
from collections import deque
from midiutil import MIDIFile
from pydub import AudioSegment
import time

"""
Create audio from EEG data using MIDI and convert to MP3

MacOS
1. Install fluidsynth using Homebrew:
   $ brew install fluidsynth

Windows
1. Download Fluidsynth for Windows 10 here:  https://github.com/FluidSynth/fluidsynth/releases
2. Extract the contents of the ZIP file to a folder on your computer, C:/Program Files/fluidsynth
3. Open Start Menu and search "Environment Variables". Under System Variables, find Path, click Edit and add:
   C:/Program Files/fluidsynth/bin
4. Test by opening a new Command Prompt and typing: $ fluidsynth --version
5. Download SDL3 from the official site: https://github.com/libsdl-org/SDL/releases
    5.1. Find the latest SDL3-devel-...-VC.zip (for Visual Studio) or SDL3-...-win32/x64.zip
    5.2. Inside the zip, you'll find a SDL3.dll file in: lib/x64/
    5.3. Copy SDL3.dll into the same folder as fluidsynth.exe, e.g., C:/Program Files/FluidSynth/bin
6. Install FFmpeg
    6.1. Go to: https://ffmpeg.org/download.html Under "Windows" → click on one of the static builds (e.g., gyan.dev)
    6.2. Download the ffmpeg-release-full.zip or ffmpeg-release-essentials.zip
    6.3. Unzip it to a folder like C:/ffmpeg
    6.4. Inside that folder, you should see ffmpeg.exe in: C:/ffmpeg/bin/ffmpeg.exe
    6.5. Open Start Menu → search “Environment Variables”
    6.7. Edit System Environment Variables → "Environment Variables"
    6.8. Under "System Variables", find and edit Path. Add: C:/ffmpeg/bin
7. Download the SoundFont file (FluidR3_GM.sf2) from: https://member.keymusician.com/Member/FluidR3_GM/index.html
8. Place the SoundFont file in the /tools/FluidR3_GM/ directory of this project
"""
 
# MIDI Note Constants
BASE_TEMPO = 15
RHYTHMS = [
    [0.25, 0.25, 0.25, 0.25],                             # Waltz (4/4)
    [0.1875, 0.1875, 0.375, 0.25],                        # Clave
    [0.125, 0.25, 0.125, 0.25, 0.25],                     # Bossa Nova
    [0.1875, 0.125, 0.1875, 0.1875, 0.3125],              # Latin Clave remix
    [0.1875, 0.1875, 0.125, 0.25, 0.25],                  # Polyrhythm
    [0.125, 0.25, 0.0625, 0.1875, 0.25, 0.125],           # Dembow
    [0.125, 0.0625, 0.1875, 0.125, 0.125, 0.25],          # Shuffle
    [0.0625, 0.1875, 0.0625, 0.0625, 0.125, 0.125, 0.375],# Breakbeat
    [0.0625, 0.125, 0.0625, 0.125, 0.125, 0.125, 0.375],  # Amen Break
    [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]  # Swing
]

BASE_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
 
SOUNDFONT_PATH = "tools/module90/module90.sf2"
WAV_FILE = "artifacts/audio-happy.wav"
MP3_FILE = "artifacts/audio-happy.mp3"

def build_pentatonic_scale(pitch, base_scale):
    # Pentatonic minor steps in semitones: 0, 3, 5, 7, 10
    PENTATONIC_INTERVALS = [0, 3, 5, 7, 10]
    
    scale = []
    octave_range = 2
    base_note_in_octave = (pitch % 12) * 5

    # Continue adding notes across octaves
    for octave_count in range(octave_range - 1):
        for interval in PENTATONIC_INTERVALS:
            note = octave_count * 12 + base_note_in_octave + interval
            scale.append(note)
    return scale


def adjust_pitch(pitch, SCALE):
    from bisect import bisect_left

    min_scale = min(SCALE)
    max_scale = max(SCALE)

    def closest_transposed(note, direction='down'):
        if direction == 'down':
            transpositions = range(note, 0, -12)
        else:
            transpositions = range(note, pitch + 49, 12)
        return min(
            transpositions,
            key=lambda t: (abs(pitch - t), t > pitch)  # prefer ≤ pitch if equally close
        )

    if pitch < min_scale:
        best_note = min(
            SCALE,
            key=lambda n: (abs(pitch - closest_transposed(n, 'down')), closest_transposed(n, 'down') > pitch)
        )
        return best_note

    elif pitch > max_scale:
        best_note = min(
            SCALE,
            key=lambda n: (abs(pitch - closest_transposed(n, 'up')), closest_transposed(n, 'up') > pitch)
        )
        return best_note

    else:
        # Mid-range pitch: remainder logic
        best_note = min(SCALE, key=lambda x: (pitch % x, SCALE.index(x)))
        return best_note

 
def normalize_data(data, min_val, max_val):
    data = np.array(data)
    data_min = data.min()
    data_max = data.max()
    if data_min == data_max:
        return np.full_like(data, (min_val + max_val) // 2)
    normalized = (data - data_min) / (data_max - data_min)
    scaled = (normalized * (max_val - min_val) + min_val)
    return scaled.astype(int)
 

def create_midi(input_file, output_file):
    print("Creating modular-inspired MIDI...")

    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Skip headers

        max_samples = 500
        channels = ['O1', 'O2', 'T3', 'T4']
        channel_data = {ch: deque(maxlen=max_samples) for ch in channels}

        for row in reader:
            if len(row) == len(channels):
                for i, channel in enumerate(channels):
                    channel_data[channel].append(float(row[i]))

    # Presets for MIDI Track
    pitches = normalize_data(channel_data['O1'], 0, 127)
    note_duration = normalize_data(channel_data['T4'], 0, 9)
    velocities = 127
    scale_choice = build_pentatonic_scale(pitches[0], BASE_SCALE)
    current_index = 0
    rhythm_step = 0
    current_rhythm = RHYTHMS[note_duration[current_index]]

    midi_file = MIDIFile(1)
    track, channel, time = 0, 0, 0

    midi_file.addTempo(track, time, BASE_TEMPO)

    for i, pitch in enumerate(pitches):
        duration = current_rhythm[rhythm_step]
        pitch = adjust_pitch(pitch, scale_choice)

        midi_file.addNote(track, channel, pitch, time, duration, velocities)
        time += duration  # advance time by actual rhythm step


        # Advance rhythm step, and switch rhythm if it's complete
        rhythm_step += 1
        if rhythm_step >= len(current_rhythm):
            current_index = (current_index + 1) % len(note_duration)
            current_rhythm = RHYTHMS[note_duration[current_index]]
            rhythm_step = 0

    with open(output_file, "wb") as file:
        midi_file.writeFile(file)

    print(f"MIDI file saved: {output_file}")


def convert_midi_to_mp3(midi_file, soundfont_path, wav_output, mp3_output):
    # Get the correct executable name (Windows needs .exe)
    fluidsynth_cmd = "fluidsynth.exe" if platform.system() == "Windows" else "fluidsynth"

    # Step 1: Convert MIDI to WAV
    subprocess.run([
        fluidsynth_cmd,
        "-ni", 
        soundfont_path,
        midi_file,
        "-F", wav_output,
        "-r", "44100"
    ], check=True)

    # Step 2: Convert WAV to MP3
    audio = AudioSegment.from_wav(wav_output)
    audio.export(mp3_output, format="mp3")

    print(f"✅ Done! MP3 saved to: {mp3_output}")

def create_audio(input_file, output_file):
    create_midi(input_file, output_file)
    convert_midi_to_mp3(output_file, SOUNDFONT_PATH, WAV_FILE, MP3_FILE)
    time.sleep(7)
