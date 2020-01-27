#!/usr/bin/env python3

import os
import sys
import time
import pyaudio
import numpy as np

null_fd = os.open(os.devnull, os.O_RDWR)
saved_fd = os.dup(2)
os.dup2(null_fd, 2)

p = pyaudio.PyAudio()

stream =  p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True)

note_frequencies =  {
    'A': 27.50000,
    'B': 30.86771,
    'C': 16.35160,
    'D': 18.35405,
    'E': 20.60172,
    'F': 21.82676,
    'G': 24.49971
}

DEFAULT_OCTAVE = 4
RATE = 44100
VOLUME = 0.4

def print_note_error(substr: str):
    error = str.encode("Error: invalid note format: '" + substr + "' in '" + note + "'" + os.linesep)
    os.write(saved_fd, error)

def print_duration_error():
    error = str.encode("Error: invalid duration format in '" + duration + "'" + os.linesep)
    os.write(saved_fd, error)

def try_help_message():
    message = str.encode("Try '" + os.path.basename(__file__) + " --help'" + os.linesep)
    os.write(saved_fd, message)

def set_semitone(freq: float, symbol: str):
    if freq == 0:
        return freq
    if symbol == '#':
        freq *= (2 ** (1. / 12.))
    elif symbol == 'b':
        freq /= (2 ** (1. / 12.))
    else:
        print_note_error(symbol)
        freq = 0
    return freq

def set_octave(freq: float, octave: str):
    if freq == 0:
        return freq
    try:
        octave_value = int(octave)
        if octave_value < 0 or octave_value > 8:
            raise ValueError('octave value error')
        freq *= (2 ** octave_value)
    except:
        print_note_error(octave)
        freq = 0
    return freq

def set_frequency(letter: str):
    upper_case_letter = letter.upper()
    try:
        freq = note_frequencies[upper_case_letter]
    except:
        print_note_error(letter)
        freq = 0
    return freq

def compute_note(note: str):
    freq = set_frequency(note[:1])
    if len(note) == 1:
        freq = set_octave(freq, DEFAULT_OCTAVE)
    elif len(note) == 2:
        if note[1:2] == '#' or note[1:2] == 'b':
            freq = set_octave(freq, DEFAULT_OCTAVE)
            freq = set_semitone(freq, note[1:2])
        else:
            freq = set_octave(freq, note[1:2])
    elif len(note) == 3:
        freq = set_octave(freq, note[1:2])
        freq = set_semitone(freq, note[2:3])
    else:
        error = str.encode("Error: invalid format for the '" + note + "' note" + os.linesep)
        os.write(saved_fd, error)
        try_help_message()
    return freq

def play_sound(freq: float, duration: float):
    frames = [np.sin(np.arange(int(duration * RATE)) * (float(freq) * (np.pi * 2) / RATE)).astype(np.float32)]
    frames = np.concatenate(frames) * VOLUME
    fade = 1000
    fade_in = np.arange(0., 1., 1/fade)
    fade_out = np.arange(1., 0., -1/fade)
    frames[:fade] = np.multiply(frames[:fade], fade_in)
    frames[-fade:] = np.multiply(frames[-fade:], fade_out)
    stream.write(frames.tostring())

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
            print_duration_error()
            freq = 0
        if freq != 0:
            play_sound(freq, duration_value)

time.sleep(0.1)
stream.stop_stream()
stream.close()
p.terminate()

os.dup2(saved_fd, 2)
os.close(null_fd)