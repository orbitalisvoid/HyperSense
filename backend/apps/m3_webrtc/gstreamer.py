import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst, GstRtspServer  # errors are fine, still run -> so bad


class VideoRTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        super().__init__()

    def do_create_element(self, url):
        # defines where to ingest the stream from -> need to learn the pipeline syntax
        pipeline = (
            "rtspsrc location=rtsp://localhost:50000/cam1 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! x264enc bitrate=1000 ! "
            "rtph264pay name=pay0 pt=96"
        )
        return Gst.parse_launch(pipeline)


def main():
    Gst.init(None)
    loop = GLib.MainLoop()

    server = GstRtspServer.RTSPServer()
    server.set_service("9554")

    factory = VideoRTSPMediaFactory()
    mounts = server.get_mount_points()
    mounts.add_factory("/stream", factory)

    # server start
    server.attach(None)

    print("RTSP server is running at rtsp://localhost:9554/cam1-stream")

    loop.run()
