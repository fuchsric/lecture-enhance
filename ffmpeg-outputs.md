# Example ffmpeg outputs

As reference for developers, this file contains example text-outputs of different ffmpeg commands.

## ffprobe

```
$ ffprobe -hide_banner -show_streams -print_format json -i example.mp4 2>/dev/null
{
    "streams": [
        {
            "index": 0,
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "profile": "Constrained Baseline",
            "codec_type": "video",
            "codec_time_base": "1001/60000",
            "codec_tag_string": "avc1",
            "codec_tag": "0x31637661",
            "width": 900,
            "height": 720,
            "coded_width": 900,
            "coded_height": 720,
            "has_b_frames": 0,
            "sample_aspect_ratio": "178:163",
            "display_aspect_ratio": "445:326",
            "pix_fmt": "yuv420p",
            "level": 31,
            "chroma_location": "left",
            "refs": 1,
            "is_avc": "true",
            "nal_length_size": "4",
            "r_frame_rate": "30000/1001",
            "avg_frame_rate": "30000/1001",
            "time_base": "1/30000",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 164558400,
            "duration": "5485.280000",
            "bit_rate": "2293136",
            "bits_per_raw_sample": "8",
            "nb_frames": "164394",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "VideoHandler"
            }
        },
        {
            "index": 1,
            "codec_name": "aac",
            "codec_long_name": "AAC (Advanced Audio Coding)",
            "profile": "LC",
            "codec_type": "audio",
            "codec_time_base": "1/48000",
            "codec_tag_string": "mp4a",
            "codec_tag": "0x6134706d",
            "sample_fmt": "fltp",
            "sample_rate": "48000",
            "channels": 1,
            "channel_layout": "mono",
            "bits_per_sample": 0,
            "r_frame_rate": "0/0",
            "avg_frame_rate": "0/0",
            "time_base": "1/48000",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 263294976,
            "duration": "5485.312000",
            "bit_rate": "82598",
            "max_bit_rate": "128000",
            "nb_frames": "257124",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "SoundHandler"
            }
        }
    ]
}
```

## showinfo

```
$ ffmpeg -hide_banner -nostdin -i example.mp4 -frames:v 1 -vf fifo,showinfo -f null - >/dev/null
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'example.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf54.11.100
  Duration: 01:31:25.31, start: 0.000000, bitrate: 2382 kb/s
    Stream #0:0(und): Video: h264 (Constrained Baseline) (avc1 / 0x31637661), yuv420p, 900x720 [SAR 178:163 DAR 445:326], 2293 kb/s, 29.97 fps, 29.97 tbr, 30k tbn, 59.94 tbc (default)
    Metadata:
      handler_name    : VideoHandler
    Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, mono, fltp, 82 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
Stream mapping:
  Stream #0:0 -> #0:0 (h264 (native) -> wrapped_avframe (native))
  Stream #0:1 -> #0:1 (aac (native) -> pcm_s16le (native))
[Parsed_showinfo_1 @ 0x7fffc9eda9a0] config in time_base: 1/30000, frame_rate: 30000/1001
[Parsed_showinfo_1 @ 0x7fffc9eda9a0] config out time_base: 0/0, frame_rate: 0/0
Output #0, null, to 'pipe:':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf57.83.100
    Stream #0:0(und): Video: wrapped_avframe, yuv420p, 900x720 [SAR 178:163 DAR 445:326], q=2-31, 200 kb/s, 29.97 fps, 29.97 tbn, 29.97 tbc (default)
    Metadata:
      handler_name    : VideoHandler
      encoder         : Lavc57.107.100 wrapped_avframe
    Stream #0:1(und): Audio: pcm_s16le, 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      encoder         : Lavc57.107.100 pcm_s16le
[Parsed_showinfo_1 @ 0x7fffc9eda9a0] n:   0 pts:      0 pts_time:0       pos:      277 fmt:yuv420p sar:178/163 s:900x720 i:P iskey:1 type:I checksum:D52BBFA1 plane_checksum:[C72ACDCF B6EE2068 6E7CD15B] mean:[95 125 125] stdev:[72.1 8.3 8.6]
frame=    1 fps=0.0 q=-0.0 Lsize=N/A time=00:00:00.29 bitrate=N/A speed=7.19x
video:1kB audio:26kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: unknown
```

## silencedetect

```
$ ffmpeg -hide_banner -nostdin -i example.mp4 -vn -af silencedetect=n=-40dB:d=0.2 -f null - >/dev/n
ull
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'example.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf54.11.100
  Duration: 01:31:25.31, start: 0.000000, bitrate: 2382 kb/s
    Stream #0:0(und): Video: h264 (Constrained Baseline) (avc1 / 0x31637661), yuv420p, 900x720 [SAR 178:163 DAR 445:326], 2293 kb/s, 29.97 fps, 29.97 tbr, 30k tbn, 59.94 tbc (default)
    Metadata:
      handler_name    : VideoHandler
    Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, mono, fltp, 82 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
Stream mapping:
  Stream #0:1 -> #0:0 (aac (native) -> pcm_s16le (native))
Output #0, null, to 'pipe:':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf57.83.100
    Stream #0:0(und): Audio: pcm_s16le, 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      encoder         : Lavc57.107.100 pcm_s16le
[silencedetect @ 0x7fffe4c517c0] silence_start: 20.3227
[silencedetect @ 0x7fffe4c517c0] silence_end: 20.8853 | silence_duration: 0.562667
[silencedetect @ 0x7fffe4c517c0] silence_start: 30.9253
[silencedetect @ 0x7fffe4c517c0] silence_end: 31.296 | silence_duration: 0.370667
[silencedetect @ 0x7fffe4c517c0] silence_start: 37.304
[silencedetect @ 0x7fffe4c517c0] silence_end: 37.9093 | silence_duration: 0.605333
[silencedetect @ 0x7fffe4c517c0] silence_start: 43.576
[silencedetect @ 0x7fffe4c517c0] silence_end: 44.4373 | silence_duration: 0.861333
[silencedetect @ 0x7fffe4c517c0] silence_start: 50.4027
[silencedetect @ 0x7fffe4c517c0] silence_end: 50.7733 | silence_duration: 0.370667
[silencedetect @ 0x7fffe4c517c0] silence_start: 50.7653
[silencedetect @ 0x7fffe4c517c0] silence_end: 51.0933 | silence_duration: 0.328

*** many lines ommitted for brevity ***

[silencedetect @ 0x7fffe4c517c0] silence_start: 5474.85
[silencedetect @ 0x7fffe4c517c0] silence_end: 5475.2 | silence_duration: 0.349333
[silencedetect @ 0x7fffe4c517c0] silence_start: 5475.41
[silencedetect @ 0x7fffe4c517c0] silence_end: 5475.88 | silence_duration: 0.477333
[silencedetect @ 0x7fffe4c517c0] silence_start: 5475.9
[silencedetect @ 0x7fffe4c517c0] silence_end: 5476.16 | silence_duration: 0.264
[silencedetect @ 0x7fffe4c517c0] silence_start: 5476.39
[silencedetect @ 0x7fffe4c517c0] silence_end: 5476.69 | silence_duration: 0.306667
[silencedetect @ 0x7fffe4c517c0] silence_start: 5477.65
[silencedetect @ 0x7fffe4c517c0] silence_end: 5478.27 | silence_duration: 0.626667
size=N/A time=01:31:25.31 bitrate=N/A speed= 766x
video:0kB audio:514246kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: unknown
```
