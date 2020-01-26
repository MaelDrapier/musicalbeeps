#!/usr/bin/env python3

import os
import sys

null_fd = os.open(os.devnull, os.O_RDWR)
saved_fd = os.dup(2)
os.dup2(null_fd, 2)

from pysine import sine


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

def print_format_error(substr: str):
    error = str.encode("Error: invalid note format: '" + substr + "' in '" + note + "'")
    os.write(saved_fd, error)

def set_semitone(freq: float, symbol: str):
    if freq == 0:
        return freq
    if symbol == '#':
        freq *= (2 ** (1. / 12.))
    elif symbol == 'b':
        freq /= (2 ** (1. / 12.))
    else:
        print_format_error(symbol)
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
        print_format_error(octave)
        freq = 0
    return freq

def set_frequency(letter: str):
    upper_case_letter = letter.upper()
    try:
        freq = note_frequencies[upper_case_letter]
    except:
        print_format_error(letter)
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
        print('333')
    return freq

freq = 440.0
for line in sys.stdin:
    line = line.rstrip()
    note, duration = line.split('-')
    freq = compute_note(note)
    sine(freq, 0.5)

os.dup2(saved_fd, 2)
os.close(null_fd)