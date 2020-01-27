#!/usr/bin/env python3

import os
import sys
import time
import pyaudio
import numpy as np
import argparse

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
glob_null_fd = os.open(os.devnull, os.O_RDWR)
glob_error_fd = os.dup(2)
os.dup2(glob_null_fd, 2)

def setup_argparse():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='''\
    A python script playing musical notes

how to use:
    Notes are read from a file passed as argument, or directly from the
    standard input. Each note must be on a new line.

note format:
    Each note must be formatted like so: 'A5#:1.5' (without quotes)
    Where:
        - 'A' is the note (between A and G, can be lowercase)
        - '5' is the octave (between 0 and 8, default=4)
        - '#' (or 'b') is optional and used to play a sharp or flat note
        - ':1.5' is the duration of the note (1.5 seconds here, default=0.5)

sleep:
    You can pause the player by replacing the note by the 'sleep' word.
    For exemple, 'sleep:5' will pause the player for 5 seconds.
    ''')
    parser.add_argument("file",
                        nargs="?",
                        help="a file containing music notes")
    parser.add_argument("--silent",
                        help="disable player output",
                        action='store_true')
    args = parser.parse_args()
    if args.file:
        input_file = open(args.file, 'r')
    else:
        input_file = sys.stdin
    return args, input_file

def print_note_error(substr: str, line: str):
    error = str.encode("Error: invalid note format: '" + substr + "' in '" + line + "'" + os.linesep)
    os.write(glob_error_fd, error)

def print_duration_error(duration: str, line: str):
    error = str.encode("Error: invalid duration format: '" + duration + "' in '" + line + "'" + os.linesep)
    os.write(glob_error_fd, error)

def print_played_note(args, note: str, duration: float):
    if not args.silent:
        if note == 'sleep':
            print("Sleeping (" + str(duration) + "s)")
        else:
            print("Playing " + note + " (" + str(duration) + "s)")


def set_semitone(freq: float, symbol: str, note: str, line: str):
    if freq == 0:
        return freq
    if symbol == '#':
        freq *= (2 ** (1. / 12.))
    elif symbol == 'b':
        freq /= (2 ** (1. / 12.))
    else:
        print_note_error(symbol, line)
        freq = 0
    return freq

def set_octave(freq: float, octave: str, note: str, line: str):
    if freq == 0:
        return freq
    try:
        octave_value = int(octave)
        if octave_value < 0 or octave_value > 8:
            raise ValueError('octave value error')
        freq *= (2 ** octave_value)
    except:
        print_note_error(octave, line)
        freq = 0
    return freq

def set_frequency(letter: str, note: str, line: str):
    upper_case_letter = letter.upper()
    try:
        freq = note_frequencies[upper_case_letter]
    except:
        print_note_error(letter, line)
        freq = 0
    return freq

def compute_note(note: str, line: str):
    freq = set_frequency(note[:1], note, line)
    if len(note) == 1:
        freq = set_octave(freq, DEFAULT_OCTAVE, note, line)
    elif len(note) == 2:
        if note[1:2] == '#' or note[1:2] == 'b':
            freq = set_octave(freq, DEFAULT_OCTAVE, note, line)
            freq = set_semitone(freq, note[1:2], note, line)
        else:
            freq = set_octave(freq, note[1:2], note, line)
    elif len(note) == 3:
        freq = set_octave(freq, note[1:2], note, line)
        freq = set_semitone(freq, note[2:3], note, line)
    else:
        if freq != 0:
            print_note_error(note, line)
            freq = 0
    return freq

def write_stream(stream: pyaudio.Stream, freq: float, duration: float):
    frames = [np.sin(np.arange(int(duration * RATE)) * (float(freq) * (np.pi * 2) / RATE)).astype(np.float32)]
    frames = np.concatenate(frames) * VOLUME
    fade = 1000
    fade_in = np.arange(0., 1., 1/fade)
    fade_out = np.arange(1., 0., -1/fade)
    frames[:fade] = np.multiply(frames[:fade], fade_in)
    frames[-fade:] = np.multiply(frames[-fade:], fade_out)
    stream.write(frames.tostring())

def play_note(stream: pyaudio.Stream, note: str, freq: float, duration: float):
    if note == 'sleep':
        time.sleep(duration)
    else:
        write_stream(stream, freq, duration)

def player_loop(args, input_file, stream: pyaudio.Stream):
    freq = 440.0
    for line in input_file:
        line = line.rstrip()
        if len(line) > 0:
            try:
                note, duration = line.split(':')
            except:
                note, duration = line, '.5'
            if note != 'sleep':
                freq = compute_note(note, line)
            try:
                duration_value = float(duration)
            except:
                print_duration_error(duration, line)
                freq = 0
            if freq != 0:
                print_played_note(args, note, duration_value)
                play_note(stream, note, freq, duration_value)
    if not args.silent:
        print("Done")



def main():
    args, input_file = setup_argparse()

    # portaudio stream initialization
    p = pyaudio.PyAudio()
    stream =  p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True)

    player_loop(args, input_file, stream)

    # stop and close pyaudio
    time.sleep(0.1)
    stream.stop_stream()
    stream.close()
    p.terminate()

    if input_file is not sys.stdin:
        input_file.close

if __name__ == "__main__":
    main()

# set stderr back to its value
os.dup2(glob_error_fd, 2)
os.close(glob_null_fd)