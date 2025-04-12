```sh
$ uv sync --all-packages
```

# M2_Processing_Node

### start the RTSP server, this allows OpenCV to push frames to it, and M2 Nodes to pull frames from it

I chose to use MediaMTX because it has the ability to receive RTSP. Developing our own server can be done later once I gathered enough information and skills required. Afaik, handling all RTSP sessions takes some considerations.

```sh
$ ./tools/mediamtx apps/m2_processing_node/mediamtx.yml
2025/04/12 17:53:06 INF MediaMTX v1.11.3
2025/04/12 17:53:06 INF configuration loaded from <>/HyperSight/ai_engine/apps/m2_processing_node/mediamtx.yml
2025/04/12 17:53:06 INF [RTSP] listener opened on :8554 (TCP)
```

### the nodes process frames from rtsp://localhost:**8554**/cam1 and will push them to rtsp://localhost:**9554**/cam1
There is a race in this script, where the ingestion while-loop was running faster than the output, causing it to write duplicated frames. This is being worked on.
```sh
$ uv run start-node
```

# M3_WebRTC

### MacOS

```sh
$ brew install gstreamer
```

### start the RTSP server, this allows nodes to push frames to it, and M3 to pull frames from it

```sh
$ ./tools/mediamtx apps/m3_processing_node/mediamtx.yml
2025/04/12 17:53:06 INF MediaMTX v1.11.3
2025/04/12 17:53:06 INF configuration loaded from <>/HyperSight/ai_engine/apps/m3_webrtc/mediamtx.yml
2025/04/12 17:53:06 INF [RTSP] listener opened on :9554 (TCP)
```

### M3_WebRTC is hard-coded to pull from rtsp://localhost:9554/cam1 using Gstreamer

It is now a mini-HTTP server, which supports middlewares for Auth Token validation. The frames pulled from RTSP Server will then be forwarded via RTC tracks.

I am working on a Configurator for service discovery, all uris are hard-coded for now.

```sh
$ uv run start-webrtc
```

### test-client.html has a quick&dirty sample code to demonstrate.

Firefox has a bug: https://github.com/aiortc/aiortc/issues/481, you should open the file on another browser.
