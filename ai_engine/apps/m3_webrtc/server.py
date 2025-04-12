import asyncio
import json
import logging
from pathlib import Path

import aiohttp_cors
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame
from shared.configuration import load_config

from .stream_ingest import Pipeline, StreamIngest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HyperSight_WebRTC")


class StreamTrack(VideoStreamTrack):
    def __init__(self, _in: Pipeline):
        super().__init__()
        self._in = _in

    async def recv(self):
        while self._in.latest_frame is None:
            await asyncio.sleep(0.01)

        frame = VideoFrame.from_ndarray(self._in.latest_frame, format="rgb24")
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame


pcs = set[RTCPeerConnection]()
tracks = set[StreamTrack]()
stream_ingest: StreamIngest


async def on_shutdown(app: web.Application):
    global pcs, stream_ingest

    stream_ingest.stop()

    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


async def offer_handler(request: web.Request):
    global tracks

    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    for t in tracks:
        pc.addTrack(t)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),
    )


def main():
    global stream_ingest, tracks

    config = load_config(str(Path(__file__).parent / "config.yml"))

    # TODO: incorporate New York Configurator to discover streams
    stream_ingest = StreamIngest({"rtsp://localhost:9554/cam1"})
    stream_ingest.start()

    for p in stream_ingest.pipelines:
        tracks.add(StreamTrack(p))

    app = web.Application()
    cors = aiohttp_cors.setup(
        app,
        defaults={  # TODO: only for testing
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    app.on_shutdown.append(on_shutdown)
    cors.add(app.router.add_post("/offer", offer_handler))
    web.run_app(app, host="localhost", port=config["server"]["port"])
