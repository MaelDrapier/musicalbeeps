# MusicalBeeps

A python module to play sound beeps corresponding to musical notes from the command line or another python program.

- [Installation](#installation)
   - [From the Python Package Index](#from-the-python-package-index)
   - [From source](#from-source)
- [How to use](#how-to-use)
    - [From the command line](#from-the-command-line)
        - [Usage](#usage)
        - [Examples](#examples)
    - [From a python program](#from-a-python-program)

## Installation

### From the [Python Package Index](https://pypi.org/project/MusicalBeeps/)

`pip install musicalbeeps`

### From source

```
$ git clone https://github.com/MaelDrapier/MusicalBeeps
$ cd MusicalBeeps
$ python setup.py install
```

## How to use:

### From the command line:

#### Usage:
`musicalbeeps --help`
```
usage: musicalbeeps [-h] [--silent] [--volume VOLUME] [file]

Play sound beeps corresponding to musical notes.

positional arguments:
  file             a file containing musical notes

optional arguments:
  -h, --help       show this help message and exit
  --silent         disable player output
  --volume VOLUME  volume between 0 and 1 (default=0.5)

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
```

#### Examples:
- To play a sharp B on octave n°5 for 1.2 seconds: `echo "B5#:1.2" | musicalbeeps`

- To play the content of a file: `musicalbeeps file_to_play.txt`

Example files are provided in the [**music_scores**](music_scores) directory of this repository.


### From a python program:
```Python
import musicalbeeps


player = musicalbeeps.Player(volume = 0.3,
                            mute_output = False,
                            hide_warnings = True)

# Examples:

# To play an A on default octave n°4 for 0.2 seconds
player.play_note("A", 0.2)

# To play a G flat on octave n°3 for 2.5 seconds
player.play_note("G3b", 2.5)

# To play a F sharp on octave n°5 for the default duration of 0.5 seconds
player.play_note("F5#")

# To pause the player for 3.5 seconds
player.play_note("pause", 3.5)
```

#### Initializations parameters for the `Player` class:

|Name|Type|Default|Description|
|:---:|:---:|:---:|:---|
|`volume`|`float`|`0.5`|Set the volume. Must be between `0` and `1`|
|`mute_output`|`bool`|`False`|Mute the output displayed when a note is played|
|`hide_warnings`|`bool`|`True`|Hide warnings triggered by PortAudio by muting stderr when a note is played|
