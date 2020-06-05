#!/usr/bin/env python3.7
import click
import tempfile
import subprocess
import tqdm
import json
import inspect
import array
import math
import os
import functools


def helper_for(other):
    def decorator(f):
        @functools.wraps(f)
        def helper(*args, **kwargs):
            self = f.__name__
            helps = other.__name__
            caller = inspect.stack()[1][3]
            assert caller == helps, f"{self} is helper function for {helps}, but was called by {caller}"
            return f(*args, **kwargs)
        return helper
    return decorator


def tempfile_noise(tmpdir):
    return os.path.join(tmpdir, "noise.prof")


def tempfile_audio(tmpdir):
    return os.path.join(tmpdir, "audio.mp4")


@click.group(chain=True)
@click.option(
    '--speed',
    type=click.FloatRange(1/4, 4),
    default=1,
    help="Multiply playback speed of the video",
    show_default=True)
@click.option(
    '--pitch-shift',
    type=click.FloatRange(-1, 1),
    default=0,
    help="Change the audio pitch by a factor",
    show_default=True)
@click.option(
    '--stack',
    type=click.Choice(["horizontal", "vertical"]),
    default="horizontal",
    help="How to arrange multiple videos",
    show_default=True)
@click.option(
    '--default-filters/--no-default-filters',
    default=True,
    help="Use default highpass/lowpass filters",
    show_default=True)
@click.option(
    '--default-loudnorm/--no-default-loudnorm',
    default=True,
    help="Use default loudness normalization",
    show_default=True)
@click.option(
    '--silence-threshold',
    type=click.FloatRange(-100, 0),
    default=-40,
    help="Amplitude (in dB) that separates background noise from speech",
    show_default=True)
@click.option(
    '--silence-minimum-duration',
    type=click.FloatRange(0.01, 100),
    default=0.2,
    help="Silence shorter than this will not be cut",
    show_default=True)
@click.option(
    '--noiseremove-factor',
    type=click.FloatRange(0, 1),
    default=0.21,
    help="Strength of noise filtering",
    show_default=True)
@click.option(
    '--tmpdir',
    default=".",
    help="Folder for temporary files",
    show_default=True)
def cli(**kwargs):
    pass


@cli.command('input')
@click.argument('file')
@click.option(
    '-vf',
    default="",
    help="additional video filters")
@click.option(
    '-af',
    default="",
    help="additional audio filters")
@click.option(
    '--place',
    type=int,
    nargs=2,
    help="Manually set Y, X positions for video")
@click.option(
    '--this-audio',
    is_flag=True,
    help="If multiple input files contain audio, use this file's")
def addfile(file, vf, af, place, this_audio):
    return "in", (file, vf, af, place, this_audio)


@cli.command('output')
@click.argument('file')
@click.option(
    '-vf',
    default="",
    help="additional video filters")
@click.option(
    '-af',
    default="",
    help="additional audio filters")
def outfile(file, vf, af):
    return "out", (file, vf, af)


@cli.resultcallback()
def main(inputlist, **kwargs):
    with tempfile.TemporaryDirectory(prefix="lecture-enhance-", dir=kwargs["tmpdir"]) as tmpdir:
        duration, (w, h), videos, audio, output = preprocessOptions(inputlist, **kwargs)
        bitmap, longest_silence = findSilence(audio, **kwargs)
        analyzeNoise(audio, longest_silence, tmpdir)
        processAudio(audio, output, bitmap, tmpdir, kwargs["noiseremove_factor"])
        processVideo(videos, output, bitmap, tmpdir, w, h)
    print("all done!")


@helper_for(main)
def preprocessOptions(inputlist, **kwargs):
    videos = []
    audio = None
    output = None
    duration = 0
    used_this_audio_flag = False

    for t, i in inputlist:
        if t == "in":
            file, vf, af, place, this_audio = i

            d, (a_count, v_count), (w, h) = ffprobe(file)
            duration = max(duration, d)

            if a_count > 1 or v_count > 1:
                raise click.ClickException(
                    "multiple channels in one file are not supported: "
                    + f"\"{file}\" has {a_count} audio and {v_count} video channels")
            if a_count == 1:
                if this_audio and used_this_audio_flag:
                    raise click.ClickException(f"--this-audio was used more than once")
                if audio is None or this_audio:
                    audio = {"file": file, "af": af}
                else:
                    print(f"Warning: audio in \"{file}\" ignored")
            if v_count == 1:
                if vf != "":
                    w, h = getWH(file, vf)
                videos.append({"file": file, "vf": vf, "place": place, "w": w, "h": h})
            if a_count == 0 and v_count == 0:
                raise click.ClickException(f"\"{file}\" has no audio or video")
        elif t == "out":
            file, vf, af = i
            if output is not None:
                raise click.ClickException("only one output may be specified")
            output = {"file": file, "vf": vf, "af": af}

    af, vf = defaultFilters(**kwargs)

    if len(output["vf"]) > 0:
        vf = [output["vf"]] + vf
    if len(output["af"]) > 0:
        af = [output["af"]] + af
    output["vf"] = ",".join(vf)
    output["af"] = ",".join(af)

    videos, (w, h) = placeVideos(videos, kwargs["stack"] == "vertical")

    return duration, (w, h), videos, audio, output


@helper_for(preprocessOptions)
def ffprobe(file):
    cmd = [
        "ffprobe",
        "-hide_banner",
        "-show_streams",
        "-print_format", "json",
        "-i", file
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    res = json.loads(res.stdout)
    duration = 0
    a_count = 0
    v_count = 0
    w, h = 0, 0
    for s in res["streams"]:
        if "duration" in s:
            duration = float(s["duration"])
        if s["codec_type"] == "audio":
            a_count += 1
        elif s["codec_type"] == "video":
            v_count += 1
            w, h = s["width"], s["height"]
    return duration, (a_count, v_count), (w, h)


@helper_for(preprocessOptions)
def getWH(file, vf):
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-i", file,
        "-frames:v", "1",
        "-vf", f"{vf},showinfo",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    for line in res.stderr.decode("utf-8").split("\n"):
        if "_showinfo_" in line and " s:" in line:
            dims = line.split(" s:")[-1].split(" ")[0]
            w, h = dims.split("x")
            return int(w), int(h)
    raise click.ClickException(
        f"could not determine video dimensions for file \"{file}\" and filters \"{vf}\"")


@helper_for(preprocessOptions)
def defaultFilters(**kwargs):
    af, vf = [], []

    pitch = kwargs["pitch_shift"]
    speed = kwargs["speed"]
    samples = int(44100 * (1 - pitch))
    tempo_total = speed * (1 - pitch)
    tempo = []
    epsilon = 0.5/44100
    while tempo_total > 2:
        tempo.append(2)
        tempo_total *= 0.5
    while tempo_total < 0.5:
        tempo.append(0.5)
        tempo_total *= 2
    tempo.append(tempo_total)
    if samples != 44100:
        af.append(f"aresample={samples}")
    for t in tempo:
        if abs(t-1) > epsilon:
            af.append(f"atempo={t}")
    if samples != 44100:
        af.append("asetrate=44100")
    if kwargs["default_filters"]:
        af.append("lowpass=f=1700,highpass=f=100")
    if kwargs["default_loudnorm"]:
        af.append("loudnorm=I=-23.0:TP=-2.0:LRA=7.0:print_format=summary")
    if abs(speed-1) > epsilon:
        vf.append(f"setpts=PTS/{speed}")

    return af, vf


@helper_for(preprocessOptions)
def placeVideos(videos, vertical):
    placed = []

    if vertical:
        w = 0
        for v in videos:
            if len(v["place"]) == 0:
                w = max(w, v["w"])
        h = 0
        for v in videos:
            if len(v["place"]) == 0:
                x = (w - v["w"])//2
                v["place"] = (h, x)
                h += v["h"]
            placed.append(v)
    else:
        w = 0
        for v in videos:
            if len(v["place"]) == 0:
                v["place"] = (0, w)
                w += v["w"]
            placed.append(v)
    w, h = 0, 0

    for v in placed:
        nw, nh = v["place"][1]+v["w"], v["place"][0]+v["h"]
        w, h = max(w, nw), max(h, nh)

    return placed, (w, h)


@helper_for(main)
def findSilence(audio, **kwargs):
    print("detecting silence...")
    af = audio["af"]
    if len(af) > 0:
        af += ","
    silence_threshold = kwargs["silence_threshold"]
    minimum_duration = kwargs["silence_minimum_duration"]
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-i", audio["file"],
        "-vn",
        "-af", f"{af}silencedetect=n={silence_threshold}dB:d={minimum_duration}",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)

    silences = []
    longest_silence = (0, 0)
    start, end = None, None

    for line in res.stderr.split(b"\n"):
        if b"silencedetect" not in line:
            continue
        if b"silence_start:" in line:
            start, end = float(line.split(b" ")[-1]), None
        if b"silence_end:" in line:
            end = float(line.split(b" | ")[0].split(b" ")[-1])
            if start is not None:
                silences.append((start, end))
            if (end - start) > (longest_silence[1] - longest_silence[0]):
                longest_silence = (start, end)

    assert len(silences) > 0

    fps = 12
    N = int(math.ceil(silences[-1][1]) * fps) + 1
    bitmap = array.array('B', (0 for _ in range(N)))

    for start, end in silences:
        start, end = int(math.ceil(start * fps)), int(math.floor(end * fps))
        for i in range(start, end+1):
            bitmap[i] = 1

    print(f"found {len(silences)} pauses totaling {format_time(sum(bitmap) / fps)}")
    print(f"longest period of silence: {format_time(longest_silence[1] - longest_silence[0])}")

    return bitmap, longest_silence


@helper_for(findSilence)
def format_time(t):
    if t < 60:
        return f"{t:.1f} seconds"
    t /= 60
    if t < 60:
        return f"{t:.1f} minutes"
    t /= 60
    return f"{t:.1f} hours"


@helper_for(main)
def analyzeNoise(audio, longest_silence, tmpdir):
    print("analyzing noise...")
    start, end = longest_silence
    af = audio["af"]
    if len(af) == 0:
        af = "afifo"

    null, pipe = subprocess.DEVNULL, subprocess.PIPE
    with subprocess.Popen([
        "ffmpeg",
        "-y", "-nostdin",
        "-ss", str(start),
        "-i", audio["file"],
        "-vn",
        "-to", str(end),
        "-af", af,
        "-ar", "44100", "-ac", "1", "-f", "f32le",
        "-fflags", "+bitexact", "-flags:a", "+bitexact", "-"
    ], stdin=null, stdout=pipe, stderr=null) as ffmpeg, subprocess.Popen([
        "sox",
        "-L", "-t", "raw", "-b", "32", "-e", "floating-point",
        "-c", "1", "-r", "44100", "-",
        "-n", "noiseprof", tempfile_noise(tmpdir)
    ], stdin=pipe, stdout=null, stderr=null) as sox:
        while True:
            data = ffmpeg.stdout.read(1024)
            if not data:
                break
            sox.stdin.write(data)
        sox.stdin.close()
        assert ffmpeg.wait() == 0
        assert sox.wait() == 0


@helper_for(main)
def processAudio(audio, output, bitmap, tmpdir, noiseremove_factor):
    print("processing audio...")

    af1 = audio["af"]
    if len(af1) == 0:
        af1 = "afifo"
    af2 = output["af"]
    if len(af2) == 0:
        af2 = "afifo"

    null, pipe = subprocess.DEVNULL, subprocess.PIPE
    progress = tqdm.tqdm(total=len(bitmap), unit="f")
    with subprocess.Popen([
        "ffmpeg",
        "-y", "-nostdin",
        "-ss", "0",
        "-i", audio["file"],
        "-vn",
        "-af", af1,
        "-ar", "44100", "-ac", "1", "-f", "f32le",
        "-fflags", "+bitexact", "-flags:a", "+bitexact", "-"
    ], stdin=null, stdout=pipe, stderr=null) as ffmpeg1:
        with subprocess.Popen([
            "sox",
            "-L", "-t", "raw", "-b", "32", "-e", "floating-point",
            "-c", "1", "-r", "44100", "-",
            "-L", "-t", "raw", "-b", "32", "-e", "floating-point",
            "-c", "1", "-r", "44100", "-",
            "noisered",
            tempfile_noise(tmpdir),
            str(noiseremove_factor)
        ], stdin=ffmpeg1.stdout, stdout=pipe, stderr=null) as sox, subprocess.Popen([
            "ffmpeg",
            "-y", "-nostdin",
            "-ar", "44100", "-ac", "1", "-f", "f32le",
            "-i", "-",
            "-af", af2,
            "-c:a", "aac", "-ar", "44100", "-ac", "1", "-b:a", "64k",
            "-f", "mp4",
            tempfile_audio(tmpdir)
        ], stdin=pipe, stdout=null, stderr=null) as ffmpeg2:
            size = 4 * 44100 // 12
            i = 0
            while True:
                data = sox.stdout.read(size)
                if not data:
                    break
                if i >= len(bitmap) or bitmap[i] == 0:
                    ffmpeg2.stdin.write(data)
                i += 1
                progress.update()
            ffmpeg2.stdin.close()
            assert ffmpeg1.wait() == 0
            assert sox.wait() == 0
            assert ffmpeg2.wait() == 0
    progress.close()


@helper_for(main)
def processVideo(videos, output, bitmap, tmpdir, w, h):
    print("processing video...")

    ovf = output["vf"]
    if len(ovf) == 0:
        ovf = "fifo"

    ffmpeg1cmd = [
        "ffmpeg",
        "-y", "-nostdin"
    ]
    duration = (len(bitmap) + 1) / 12
    chain = [f"color=c=black,fps=fps=12,trim=duration={duration},scale={w}x{h},setsar=sar=1[bg0]"]
    for i, v in enumerate(videos):
        ffmpeg1cmd += [
            "-ss", "0", "-i", v["file"]
        ]
        vf = v["vf"]
        if len(vf) == 0:
            vf = "fifo"
        chain.insert(0, f"[{i}:v]{vf}[v{i}]")
        y, x = v["place"]
        chain.append(f"[bg{i}][v{i}]overlay=x={x}:y={y}[bg{i+1}]")
    ffmpeg1cmd += [
        "-filter_complex", ";".join(chain),
        "-an", "-map", f"[bg{len(videos)}]",
        "-r", "12",
        "-s", "{}x{}".format(w, h),
        "-pix_fmt", "yuv420p16le", "-f", "rawvideo", "-"
    ]

    ffmpeg2cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo", "-pix_fmt", "yuv420p16le",
        "-video_size", "{}x{}".format(w, h),
        "-framerate", "12",
        "-i", "-",
        "-f", "mp4",
        "-i", tempfile_audio(tmpdir),
        "-vf", ovf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-profile:v", "baseline",
        "-crf", "23",
        "-acodec", "copy",
        "-f", "mp4",
        "-movflags", "faststart",
        output["file"]
    ]

    null, pipe = subprocess.DEVNULL, subprocess.PIPE
    progress = tqdm.tqdm(total=len(bitmap), unit="f")
    with subprocess.Popen(ffmpeg1cmd, stdin=null, stdout=pipe, stderr=null) as ffmpeg1:
        with subprocess.Popen(ffmpeg2cmd, stdin=pipe, stdout=null, stderr=null) as ffmpeg2:
            size = w * h * 3
            i = 0
            while True:
                data = ffmpeg1.stdout.read(size)
                if not data:
                    break
                if i >= len(bitmap) or bitmap[i] == 0:
                    ffmpeg2.stdin.write(data)
                i += 1
                progress.update()
            ffmpeg2.stdin.close()
            assert ffmpeg1.wait() == 0
            assert ffmpeg2.wait() == 0
    progress.close()


if __name__ == "__main__":
    cli()
