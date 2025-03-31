import asyncio
import logging

import ffmpeg
import numpy as np
from av import VideoFrame

width, height = 640, 480
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HyperSight_WebRTC.RTPIngest")


class VideoStreamIngest:
    def __init__(self, in_port: int):
        self.in_port = in_port
        self.frames_q = asyncio.Queue()
        self._stop_event = asyncio.Event()

    def start(self):
        """Start the FFmpeg process to decode the RTP stream."""
        # TODO: NOT WORKING
        self.ffmpeg_process = (
            ffmpeg.input(f"rtp://localhost:{self.in_port}", f="rawvideo", an=True, vcodec="h264")
            .output("-", format="rawvideo")
            .run_async(pipe_stdout=True)
        )
        asyncio.create_task(self._process_frames())

    async def _process_frames(self):
        """Read a raw frame from the FFmpeg process and convert to VideoFrame."""
        while not self._stop_event.is_set():
            raw_frame = self.ffmpeg_process.stdout.read(width * height * 3)
            if len(raw_frame) == 0:
                break

            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape([height, width, 3])
            video_frame = VideoFrame.from_ndarray(frame, format="yuv420p")

            await self.frames_q.put(video_frame)

    def stop(self):
        self.ffmpeg_process.terminate()
        self._stop_event.set()
