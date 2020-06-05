# lecture-enhance

This is a tool to enhance lecture recordings. Special focus is on:

- Filtering out noise like a murmuring audience or whining/humming microphones
- Cutting out pauses
- Combining multiple video sources, like slides and camera, if availible
- Speed up (optional)
- Pitch shift (optional)
- Tiny file size, optimal for phones etc.

Use at your own risk, and keep a backup of the original video around in case something goes wrong.

lecture-enhance uses [Python](https://www.python.org/), [FFmpeg](https://ffmpeg.org/), [SoX](http://sox.sourceforge.net/), [Click](https://pypi.org/project/click/), and [tqdm](https://pypi.org/project/tqdm/).

## Windows Setup

- Download this repository (Click "Clone or Download", then "Download ZIP")
- Install [Python](https://www.python.org/downloads/)
- Get [FFmpeg](https://ffmpeg.org/download.html) and copy "ffmpeg.exe" and "ffprobe.exe" to the folder where you extracted this project
- Get [SoX](https://sourceforge.net/projects/sox/files/sox/) and extract "sox.exe" and all the ".dll"-Files next to it in the same way
- Open a Terminal ("Win"+"R", type "cmd", hit "Enter") and run the command `pip install click tqdm` (Type it in the window and press "Enter")

## Windows Usage

Just drag-and-drop your lecture recordings on "lecture-enhance.bat"

## Ubuntu Setup

```
sudo apt-get install python3.7 ffmpeg sox
python3.7 -m pip install click tqdm
```

## Help

```
Usage: lecture-enhance.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --speed FLOAT RANGE             Multiply playback speed of the video
                                  [default: 1]

  --pitch-shift FLOAT RANGE       Change the audio pitch by a factor
                                  [default: 0]

  --stack [horizontal|vertical]   How to arrange multiple videos  [default:
                                  horizontal]

  --default-filters / --no-default-filters
                                  Use default highpass/lowpass filters
                                  [default: True]

  --default-loudnorm / --no-default-loudnorm
                                  Use default loudness normalization
                                  [default: True]

  --silence-threshold FLOAT RANGE
                                  Amplitude (in dB) that separates background
                                  noise from speech  [default: -40]

  --silence-minimum-duration FLOAT RANGE
                                  Silence shorter than this will not be cut
                                  [default: 0.2]

  --noiseremove-factor FLOAT RANGE
                                  Strength of noise filtering  [default: 0.21]
  --tmpdir TEXT                   Folder for temporary files  [default: .]
  --help                          Show this message and exit.

Commands:
  input
  output
```

```
Usage: lecture-enhance.py input [OPTIONS] FILE

Options:
  -vf TEXT            additional video filters
  -af TEXT            additional audio filters
  --place INTEGER...  Manually set Y, X positions for video
  --this-audio        If multiple input files contain audio, use this file's
  --help              Show this message and exit.
```

```
Usage: lecture-enhance.py output [OPTIONS] FILE

Options:
  -vf TEXT  additional video filters
  -af TEXT  additional audio filters
  --help    Show this message and exit.
```
