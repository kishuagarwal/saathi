import cv2
from cStringIO import StringIO
import numpy as np
import pyaudio
import socket
import threading
import time
import os
import wave


class VideoRecorder:
    def __init__(self):
        self.open = True
        self.device_index = 0
        self.fps = 6
        self.fourcc = 'MJPG'
        self.frameSize = (640, 480)
        self.video_filename = 'temp_video.avi'
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(
            self.video_filename, self.video_writer, self.fps, self.frameSize
        )
        self.frame_counts = 1
        self.start_time = time.time()

    def record(self):
        global client_conn
        counter = 1

        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                self.frame_counts += 1
                counter += 1
                time.sleep(0.16)
                print(type(video_frame))
                f = StringIO()
                np.savez_compressed(f, frame=video_frame)
                f.seek(0)
                client_conn.send(f.read())
            else:
                break

    def stop(self):
        if self.open:
            self.open = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()


class AudioRecorder():
    def __init__(self):
        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = 'temp_audio.wav'
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer
        )
        self.audio_frames = []

    def record(self):
        self.stream.start_stream()
        while self.open:
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if not self.open:
                break

    def stop(self):
        if self.open:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(''.join(self.audio_frames))
            waveFile.close()

    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


def start_AVrecording(filename):
    global video_thread
    global audio_thread

    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()

    return filename


def start_video_recording(filename):
    global video_thread

    video_thread = VideoRecorder()
    video_thread.start()

    return filename


def start_audio_recording(filename):
    global audio_thread

    audio_thread = AudioRecorder()
    audio_thread.start()

    return filename


def stopAVrecording(filename):
    audio_thread.stop()
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print "total frames" + str(frame_counts)
    print "elapsed time" + str(elapsed_time)
    print 'recorded fps' + str(recorded_fps)
    video_thread.stop()

    while threading.active_count() > 1:
        time.sleep(1)


def file_manager(filename):
    local_path = os.getcwd()

    if os.path.exists(str(local_path) + "/temp_audio.wav"):
        os.remove(str(local_path) + '/temp_audio.wav')

    if os.path.exists(str(local_path) + "/temp_video.avi"):
        os.remove(str(local_path) + '/temp_video.avi')

    if os.path.exists(str(local_path) + "/temp_video2.avi"):
        os.remove(str(local_path) + '/temp_video2.avi')

    if os.path.exists(str(local_path) + "/" + filename + ".avi"):
        os.remove(str(local_path) + "/" + filename + ".avi")


if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 50007))
    server_socket.listen(1)

    client_conn, addr = server_socket.accept()
    print 'Connected to client', addr

    filename = 'default_user'
    file_manager(filename)
    start_AVrecording(filename)
    time.sleep(1)
    stopAVrecording(filename)
    print 'Done'