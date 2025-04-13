import logging
from threading import Thread

import gi
import numpy as np

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst  # errors are fine, still run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StreamIngest")


class Pipeline:
    def __init__(self, uri: str) -> None:
        logger.info(uri)
        self.uri = uri
        self._pipeline = Gst.parse_launch(
            f"rtspsrc location={uri} ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw, format=RGB ! appsink name=sink"
        )
        self.latest_frame: np.ndarray

    def _process_frame(self, sink):
        sample = sink.emit("pull-sample")
        if not sample:
            logger.error("no sample")
            return Gst.FlowReturn.ERROR

        buf = sample.get_buffer()
        if not buf:
            logger.error("get buffer failed")
            return Gst.FlowReturn.ERROR

        caps = sample.get_caps()
        if not caps:
            logger.error("no caps available")
            return Gst.FlowReturn.ERROR

        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")

        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            logger.error("Failed to map buffer!")
            return Gst.FlowReturn.ERROR

        frame = np.frombuffer(map_info.data, np.uint8).reshape((height, width, 3))
        # logger.info(frame)
        buf.unmap(map_info)

        self.latest_frame = frame.copy()
        return Gst.FlowReturn.OK

    def start(self):
        sink = self._pipeline.get_by_name("sink")
        sink.set_property("emit-signals", True)
        sink.connect("new-sample", self._process_frame)

        self._pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self._pipeline.set_state(Gst.State.NULL)


class StreamIngest:
    def __init__(self, uris: set[str]):
        """
        uri: str. Ex: rtsp://localhost:8554/cam1
        """
        Gst.init(None)
        self._loop = GLib.MainLoop()
        self._pipelines = set[Pipeline]()
        # TODO: regex match uri to prevent injection
        for uri in uris:
            p = Pipeline(uri)
            p.start()
            self._pipelines.add(p)

    @property
    def pipelines(self):
        return self._pipelines

    def start(self):
        thread = Thread(target=self._loop.run, daemon=True)
        thread.start()

    def stop(self):
        for p in self._pipelines:
            p.stop()
        self._loop.quit()

    def add_pipeline(self, p: Pipeline):
        self._pipelines.add(p)
