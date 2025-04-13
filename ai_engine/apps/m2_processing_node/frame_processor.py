import logging
import subprocess
import time
from pathlib import Path
from threading import Thread

import cv2
from shared.configuration import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HyperSight_WebRTC")

# TECHDEBT:
width, height, fps = 480, 640, 25


def capture(uri_source: str, uri_sink: str):
    global width, height, fps

    _in = cv2.VideoCapture(uri_source, cv2.CAP_FFMPEG)

    ffmpeg_cmd = [
        "ffmpeg",
        "-s",
        f"{width}x{height}",
        "-r",
        f"{fps}",
        "-i",
        "-",
        "-an",
        "-pix_fmt",
        "rgb24",
        "-c:v",
        "libx264",
        "rtsp://localhost:9554/cam1",
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    while True:
        ret, frame = _in.read()
        if not ret:
            break

        # TODO: process here
        processed_frame = frame.copy()

        process.stdin.write(processed_frame.tobytes())
        process.stdin.flush()

        # BUG: it still happens, maybe the while loop isn't sufficient
        # try to mitigate duplicated frame, because while loop is faster
        time.sleep(1.0 / fps)

    _in.release()
    process.stdin.close()
    process.wait()


def main():
    config = load_config(str(Path(__file__).parent / "config.yml"))

    uris = {("rtsp://localhost:8554/cam1", "rtsp://localhost:9554/cam1")}

    threads = set[Thread]()
    for uri in uris:
        t = Thread(target=capture, args=(uri[0], uri[1]))
        threads.add(t)
        t.start()

    for t in threads:
        t.join()
