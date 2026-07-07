# Web streaming example
# Adapted from the official picamera2 example:
# https://github.com/raspberrypi/picamera2/blob/main/examples/mjpeg_server.py
# (the legacy `picamera` package used previously does not support the
# libcamera stack on Raspberry Pi OS Bookworm and is no longer maintained)

import io
import logging
import socket
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    # Disable Nagle's algorithm: without this, small writes (each MJPEG
    # frame is sent as a header + a write) can sit buffered for tens to
    # hundreds of ms waiting to be coalesced, which is fatal for using the
    # stream to drive the robot in real time.
    disable_nagle_algorithm = True

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def local_ip():
    """Best-effort guess of this host's LAN IP (no packets are actually sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (640, 480)},
    # Let the sensor run as fast as light allows, up to its ~59fps ceiling
    # at this resolution, instead of the 30fps default -- more frames per
    # second means each individual frame is less stale by the time it's
    # captured.
    controls={"FrameDurationLimits": (16666, 33333)},
    # Fewer in-flight buffers means less depth in the capture pipeline for
    # a frame to sit in before it's encoded and sent.
    buffer_count=4,
    # queue=True (the default) holds every captured frame for the encoder
    # so none are dropped, which is right for recording but means the
    # stream falls further and further behind if the encoder/network can't
    # keep up. queue=False always encodes/sends the newest frame and drops
    # the rest, trading completeness for staying close to real time.
    queue=False,
))
output = StreamingOutput()
# A lower JPEG quality (picamera2's default is 50) produces smaller frames
# that take less time to encode and to transfer, at the cost of some image
# quality -- worth it here since the point is a responsive control feed,
# not a crisp recording.
picam2.start_recording(JpegEncoder(q=40), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    print(f'Streaming at http://{local_ip()}:{address[1]}/', flush=True)
    server.serve_forever()
finally:
    picam2.stop_recording()
