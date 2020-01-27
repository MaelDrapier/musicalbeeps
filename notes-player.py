#!/usr/bin/env python3

import os
import sys
import time
import argparse
import pyaudio
import numpy as np

class NotesPlayer:
    def __init__(self, volume: float = 0.3,
                muteOutput: bool = False,
                muteStderr: bool = True):
        self.muteStderr = muteStderr

        # hide portaudio warnings by muting stderr
        self.stderrFd = os.dup(2)
        if self.muteStderr:
            self.nullFd = os.open(os.devnull, os.O_RDWR)
            os.dup2(self.nullFd, 2)

        # frequencies for the lowest octave
        self.noteFrequencies =  {
            'A': 27.50000,
            'B': 30.86771,
            'C': 16.35160,
            'D': 18.35405,
            'E': 20.60172,
            'F': 21.82676,
            'G': 24.49971
        }

        self.volume = volume
        self.muteOutput = muteOutput
        self.rate = 44100
        self.freq = 0
        self.validNote = True

        # pyaudio stream initialization
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=pyaudio.paFloat32,
                                    channels=1,
                                    rate=self.rate,
                                    output=True)

    def __del__(self):
        # stop and close pyaudio
        time.sleep(0.1)
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

        # set stderr back to its value
        if self.muteStderr:
            os.dup2(self.stderrFd, 2)
            os.close(self.nullFd)

    def __setBaseFrequency(self, note: str):
        letter = note[:1].upper()
        try:
            self.freq = self.noteFrequencies[letter]
        except:
            self.validNote = False
            error = str.encode("Error: invalid note: '" + note[:1] + "'" + os.linesep)
            os.write(self.stderrFd, error)

    def __setOctave(self, octave: str = '4'):
        if not self.validNote:
            return
        try:
            octaveValue = int(octave)
            if octaveValue < 0 or octaveValue > 8:
                raise ValueError('octave value error')
            self.freq *= (2 ** octaveValue)
        except:
            self.validNote = False
            error = str.encode("Error: invalid octave: '" + octave + "'" + os.linesep)
            os.write(self.stderrFd, error)

    def __setSemitone(self, symbol: str):
        if not self.validNote:
            return
        if symbol == '#':
            self.freq *= (2 ** (1. / 12.))
        elif symbol == 'b':
            self.freq /= (2 ** (1. / 12.))
        else:
            self.validNote = False
            error = str.encode("Error: invalid symbol: '" + symbol + "'" + os.linesep)
            os.write(self.stderrFd, error)

    def __calc_frequency(self, note: str):
        self.__setBaseFrequency(note)
        if len(note) == 1:
            self.__setOctave()
        elif len(note) == 2:
            if note[1:2] == '#' or note[1:2] == 'b':
                self.__setOctave()
                self.__setSemitone(note[1:2])
            else:
                self.__setOctave(note[1:2])
        elif len(note) == 3:
            self.__setOctave(note[1:2])
            self.__setSemitone(note[2:3])
        else:
            self.validNote = False
            error = str.encode("Error: invalid note: '" + note + "'" + os.linesep)
            os.write(self.stderrFd, error)

    def __writeStream(self, duration: float):
        frames = [np.sin(np.arange(int(duration * self.rate)) * (float(self.freq) * (np.pi * 2) / self.rate)).astype(np.float32)]
        frames = np.concatenate(frames) * self.volume
        fade = 1000
        fade_in = np.arange(0., 1., 1/fade)
        fade_out = np.arange(1., 0., -1/fade)
        frames[:fade] = np.multiply(frames[:fade], fade_in)
        frames[-fade:] = np.multiply(frames[-fade:], fade_out)
        self.stream.write(frames.tostring())

    def __printPlayedNote(self, note: str, duration: float):
        if self.muteOutput or not self.validNote:
            return
        if note == 'pause':
            print("Pausing for " + str(duration) + "s")
        else:
            print("Playing " + note + " (" + format(self.freq, '.2f') + " Hz) for " + str(duration) + "s")

    def playNote(self, note: str, duration: float = 0.5):
        self.validNote = True
        if note == 'pause':
            self.__printPlayedNote(note, duration)
            time.sleep(duration)
        else:
            self.__calc_frequency(note)
            if self.validNote:
                self.__printPlayedNote(note, duration)
                self.__writeStream(duration)



def setupArgparse():
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

pause:
    You can pause the player by replacing the note by the 'pause' word.
    For exemple, 'pause:5' will pause the player for 5 seconds.
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


def main():
    args, input_file = setupArgparse()

    notesPlayer = NotesPlayer()

    for line in input_file:
        validDuration = True
        line = line.rstrip()
        if len(line) > 0:
            try:
                note, durationStr = line.split(':')
            except:
                note, durationStr = line, '.5'
            try:
                duration = float(durationStr)
            except:
                validDuration = False
                print('error')
            if validDuration:
                notesPlayer.playNote(note, duration)

    if not args.silent:
        print("Done")

    if input_file is not sys.stdin:
        input_file.close

if __name__ == "__main__":
    main()