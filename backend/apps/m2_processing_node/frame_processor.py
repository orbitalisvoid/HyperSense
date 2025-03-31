# import subprocess
from pathlib import Path

# from sys import stdin
from configuration import load_config

# TODO: resolution / tech debt
width, height = 640, 480


def main():
    config = load_config(str(Path(__file__).parent / "config.yaml"))

    # TODO: not working
    ffmpeg_cmd = [
        "ffmpeg",
        "-i rtp://0.0.0.0:5006",  # uri to receive
        "-f rawvideo",  # Output format: raw video
        "-pix_fmt bgr24",  # Pixel format: BGR (for OpenCV)
        f"-s {width}x{height}",  # Frame size (match your stream)
        "-",
    ]

    # process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**8)

    # while True:
    #     raw_frame = stdin.read(frame_width * frame_height * 3)

    #     if not raw_frame:
    #         break

    # TODO: process here

    # TODO: send processed frame to webrtc
