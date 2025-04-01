# mediamtx for IP CAMERA emulation
```sh
$ wget https://github.com/bluenviron/mediamtx/archive/refs/heads/main.zip

$ tar xfz mediamtx_v1.11.3_darwin_arm64.tar.gz

$ rm mediamtx_v1.11.3_darwin_arm64.tar.gz LICENSE

$ ./mediamtx
```

```sh
# need to make your own video.mp4
$ ffmpeg -re -stream_loop -1 -i video.mp4 -c copy -f rtsp rtsp://localhost:8554/mystream
```