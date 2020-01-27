#!/usr/bin/env python3

import os
import sys
import time
import pyaudio
import numpy as np

VOLUME = 0.3
DEFAULT_OCTAVE = 4
RATE = 44100

# frequencies for the lowest octave
note_frequencies =  {
    'A': 27.50000,
    'B': 30.86771,
    'C': 16.35160,
    'D': 18.35405,
    'E': 20.60172,
    'F': 21.82676,
    'G': 24.49971
}

# hide portaudio warnings by muting stderr
null_fd = os.open(os.devnull, os.O_RDWR)
error_fd = os.dup(2)
os.dup2(null_fd, 2)

# portaudio stream initialization
p = pyaudio.PyAudio()
stream =  p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True)

def print_note_error(substr: str, note: str):
    error = str.encode("Error: invalid note format: '" + substr + "' in '" + note + "'" + os.linesep)
    os.write(error_fd, error)

def print_duration_error(duration: str, note: str):
    error = str.encode("Error: invalid duration format: '" + duration + "' in '" + note + "'" + os.linesep)
    os.write(error_fd, error)

def try_help_message():
    message = str.encode("Try '" + os.path.basename(__file__) + " --help'" + os.linesep)
    os.write(error_fd, message)

def set_semitone(freq: float, symbol: str, note: str):
    if freq == 0:
        return freq
    if symbol == '#':
        freq *= (2 ** (1. / 12.))
    elif symbol == 'b':
        freq /= (2 ** (1. / 12.))
    else:
        print_note_error(symbol, note)
        freq = 0
    return freq

def set_octave(freq: float, octave: str, note: str):
    if freq == 0:
        return freq
    try:
        octave_value = int(octave)
        if octave_value < 0 or octave_value > 8:
            raise ValueError('octave value error')
        freq *= (2 ** octave_value)
    except:
        print_note_error(octave, note)
        freq = 0
    return freq

def set_frequency(letter: str, note: str):
    upper_case_letter = letter.upper()
    try:
        freq = note_frequencies[upper_case_letter]
    except:
        print_note_error(letter, note)
        freq = 0
    return freq

def compute_note(note: str):
    freq = set_frequency(note[:1], note)
    if len(note) == 1:
        freq = set_octave(freq, DEFAULT_OCTAVE, note)
    elif len(note) == 2:
        if note[1:2] == '#' or note[1:2] == 'b':
            freq = set_octave(freq, DEFAULT_OCTAVE, note)
            freq = set_semitone(freq, note[1:2], note)
        else:
            freq = set_octave(freq, note[1:2], note)
    elif len(note) == 3:
        freq = set_octave(freq, note[1:2], note)
        freq = set_semitone(freq, note[2:3], note)
    else:
        error = str.encode("Error: invalid format for the '" + note + "' note" + os.linesep)
        os.write(error_fd, error)
        try_help_message()
    return freq

def play_sound(stream: pyaudio.Stream, freq: float, duration: float):
    frames = [np.sin(np.arange(int(duration * RATE)) * (float(freq) * (np.pi * 2) / RATE)).astype(np.float32)]
    frames = np.concatenate(frames) * VOLUME
    fade = 1000
    fade_in = np.arange(0., 1., 1/fade)
    fade_out = np.arange(1., 0., -1/fade)
    frames[:fade] = np.multiply(frames[:fade], fade_in)
    frames[-fade:] = np.multiply(frames[-fade:], fade_out)
    stream.write(frames.tostring())

# player loop
for line in sys.stdin:
    line = line.rstrip()
    if len(line) > 0:
        try:
            note, duration = line.split('-')
        except:
            note, duration = line, '.5'
        freq = compute_note(note)
        try:
            duration_value = float(duration)
        except:
            print_duration_error(duration, note)
            freq = 0
        if freq != 0:
            print("Playing " + note + " (" + str(duration_value) + "s)")
            play_sound(stream, freq, duration_value)

print("Done")

# stop and close pyaudio
time.sleep(0.1)
stream.stop_stream()
stream.close()
p.terminate()

# set stderr back to its value
os.dup2(error_fd, 2)
os.close(null_fd)