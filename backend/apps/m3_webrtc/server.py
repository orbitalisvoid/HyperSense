import asyncio
import json
import logging
from pathlib import Path

import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import MediaStreamTrack
from configuration import load_config
from websockets import ServerConnection

from .stream_ingest import VideoStreamIngest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HyperSight_WebRTC")

config = load_config(str(Path(__file__).parent / "config.yaml"))


class StreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, _in: VideoStreamIngest):
        super().__init__()
        self._in = _in

    async def recv(self):
        """Fetch frame from the FFmpeg ingestion queue."""
        return await self._in.frames_q.get()


async def handle_signaling(websocket: ServerConnection):
    peer_connection = RTCPeerConnection()
    logger.info(peer_connection)

    # TODO: incorporate New York Configurator to discover ports -> DevOps config.yaml
    rtp_ingests = {VideoStreamIngest(50000)}
    for ri in rtp_ingests:
        ri.start()

    tracks = (StreamTrack(ri) for ri in rtp_ingests)
    for t in tracks:
        peer_connection.addTrack(t)

    async for message in websocket:
        data = json.loads(message)
        logger.debug(data)

        if data["type"] == "offer":
            offer = RTCSessionDescription(sdp=data["sdp"], type="offer")
            await peer_connection.setRemoteDescription(offer)

            answer = await peer_connection.createAnswer()
            await peer_connection.setLocalDescription(answer)

            await websocket.send(
                json.dumps({"type": "answer", "sdp": peer_connection.localDescription.sdp})
            )


async def start_server():
    async with websockets.serve(handle_signaling, "localhost", config["server"]["port"]):
        await asyncio.Future()


def main():
    asyncio.run(start_server())
