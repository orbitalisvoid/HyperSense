# mediamtx for IP CAMERA emulation
```sh
$ wget https://github.com/bluenviron/mediamtx/releases/download/v1.11.3/mediamtx_v1.11.3_darwin_arm64.tar.gz

$ tar xfz mediamtx_v1.11.3_darwin_arm64.tar.gz

$ rm mediamtx_v1.11.3_darwin_arm64.tar.gz LICENSE

$ ./mediamtx
```

```sh
# need to make your own video.mp4, I trimmed audio from my mp4, did not test with audio
$ ffmpeg -re -stream_loop -1 -i video.mp4 -c copy -f rtsp rtsp://localhost:8554/mystream
```