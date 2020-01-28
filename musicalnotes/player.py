#!/usr/bin/env python3

import os
import time
import pyaudio
import numpy as np


class Player:
    def __init__(self, volume: float = 0.5,
                mute_output: bool = False,
                mute_stderr: bool = True):
        self.mute_stderr = False

        if volume < 0 or volume > 1:
            raise ValueError("Volume must be a float between 0 and 1")

        # Hide portaudio warnings by muting stderr
        self.mute_stderr = mute_stderr
        self.stderr_fd = os.dup(2)
        if self.mute_stderr:
            self.null_fd = os.open(os.devnull, os.O_RDWR)
            os.dup2(self.null_fd, 2)

        # Frequencies for the lowest octave
        self.note_frequencies =  {
            'A': 27.50000,
            'B': 30.86771,
            'C': 16.35160,
            'D': 18.35405,
            'E': 20.60172,
            'F': 21.82676,
            'G': 24.49971
        }

        self.volume = volume
        self.mute_output = mute_output
        self.rate = 44100
        self.freq = 0
        self.valid_note = True

        # PyAudio stream initialization
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=pyaudio.paFloat32,
                                        channels=1,
                                        rate=self.rate,
                                        output=True)

    def __set_base_frequency(self, note: str):
        letter = note[:1].upper()
        try:
            self.freq = self.note_frequencies[letter]
        except:
            self.valid_note = False
            error = str.encode("Error: invalid note: '"
                                + note[:1]
                                + "'"
                                + os.linesep)
            os.write(self.stderr_fd, error)

    def __set_octave(self, octave: str = '4'):
        if not self.valid_note:
            return
        try:
            octaveValue = int(octave)
            if octaveValue < 0 or octaveValue > 8:
                raise ValueError('octave value error')
            self.freq *= (2 ** octaveValue)
        except:
            self.valid_note = False
            error = str.encode("Error: invalid octave: '"
                                + octave
                                + "'"
                                + os.linesep)
            os.write(self.stderr_fd, error)

    def __set_semitone(self, symbol: str):
        if not self.valid_note:
            return
        if symbol == '#':
            self.freq *= (2 ** (1. / 12.))
        elif symbol == 'b':
            self.freq /= (2 ** (1. / 12.))
        else:
            self.valid_note = False
            error = str.encode("Error: invalid symbol: '"
                                + symbol
                                + "'"
                                + os.linesep)
            os.write(self.stderr_fd, error)

    def __calc_frequency(self, note: str):
        self.__set_base_frequency(note)
        if len(note) == 1:
            self.__set_octave()
        elif len(note) == 2:
            if note[1:2] == '#' or note[1:2] == 'b':
                self.__set_octave()
                self.__set_semitone(note[1:2])
            else:
                self.__set_octave(note[1:2])
        elif len(note) == 3:
            self.__set_octave(note[1:2])
            self.__set_semitone(note[2:3])
        else:
            if self.valid_note:
                error = str.encode("Errror: invalid note: '"
                                    + note
                                    + "'"
                                    + os.linesep)
                os.write(self.stderr_fd, error)
                self.valid_note = False

    def __write_stream(self, duration: float):
        frames = [np.sin(np.arange(int(duration * self.rate))
            * (float(self.freq)
            * (np.pi * 2) / self.rate)).astype(np.float32)]
        frames = np.concatenate(frames) * self.volume
        fade = 1000
        fade_in = np.arange(0., 1., 1/fade)
        fade_out = np.arange(1., 0., -1/fade)
        frames[:fade] = np.multiply(frames[:fade], fade_in)
        frames[-fade:] = np.multiply(frames[-fade:], fade_out)
        self.stream.write(frames.tostring())

    def __print_played_note(self, note: str, duration: float):
        if self.mute_output or not self.valid_note:
            return
        if note == 'pause':
            print("Pausing for " + str(duration) + "s")
        else:
            print("Playing " + note + " (" + format(self.freq, '.2f') + " Hz) for " + str(duration) + "s")

    def play_note(self, note: str, duration: float = 0.5):
            self.valid_note = True
            if note == 'pause':
                self.__print_played_note(note, duration)
                time.sleep(duration)
            else:
                self.__calc_frequency(note)
                if self.valid_note:
                    self.__print_played_note(note, duration)
                    self.__write_stream(duration)


    def __del__(self):
        # Stop and close pyaudio
        if hasattr(self, 'pyaudio') and hasattr(self, 'stream'):
            time.sleep(0.1)
            self.stream.stop_stream()
            self.stream.close()
            self.pyaudio.terminate()

        # Set stderr back to its value
        if self.mute_stderr:
            os.dup2(self.stderr_fd, 2)
            os.close(self.null_fd)