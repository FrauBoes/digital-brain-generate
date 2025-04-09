import csv
import platform
import subprocess
from collections import deque
from midiutil import MIDIFile
from pydub import AudioSegment

'''
Create audio from EEG data using MIDI and convert to MP3

MacOS
1. Install fluidsynth using Homebrew:
   $ brew install fluidsynth

Windows
1. Download Fluidsynth for Windows 10 here:  https://github.com/FluidSynth/fluidsynth/releases
2. Extract the contents of the ZIP file to a folder on your computer, C:\Program Files\fluidsynth
3. Open Start Menu and search "Environment Variables". Under System Variables, find Path, click Edit and add:
   C:\Program Files\fluidsynth\bin
4. Test by opening a new Command Prompt and typing: $ fluidsynth --version
5. Download SDL3 from the official site: https://github.com/libsdl-org/SDL/releases
    5.1. Find the latest SDL3-devel-...-VC.zip (for Visual Studio) or SDL3-...-win32/x64.zip
    5.2. Inside the zip, you'll find a SDL3.dll file in: lib\x64\
    5.3. Copy SDL3.dll into the same folder as fluidsynth.exe, e.g., C:\Program Files\FluidSynth\bin
6. Install FFmpeg
    6.1. Go to: https://ffmpeg.org/download.html Under "Windows" → click on one of the static builds (e.g., gyan.dev)
    6.2. Download the ffmpeg-release-full.zip or ffmpeg-release-essentials.zip
    6.3. Unzip it to a folder like C:\ffmpeg
    6.4. Inside that folder, you should see ffmpeg.exe in: C:\ffmpeg\bin\ffmpeg.exe
    6.5. Open Start Menu → search “Environment Variables”
    6.7. Edit System Environment Variables → "Environment Variables"
    6.8. Under "System Variables", find and edit Path. Add: C:\ffmpeg\bin
7. Download the SoundFont file (FluidR3_GM.sf2) from: https://member.keymusician.com/Member/FluidR3_GM/index.html
8. Place the SoundFont file in the /tools/FluidR3_GM/ directory of this project
'''
 
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

SOUNDFONT_PATH = "tools/FluidR3_GM/FluidR3_GM.sf2"
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
    # Get the correct executable name (Windows needs .exe)
    fluidsynth_cmd = "fluidsynth.exe" if platform.system() == "Windows" else "fluidsynth"

    # Step 1: Convert MIDI to WAV
    subprocess.run([
        fluidsynth_cmd,
        "-ni", soundfont_path,
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