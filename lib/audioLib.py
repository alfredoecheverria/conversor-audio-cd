from datetime import datetime
import threading
import queue
import sys

import soundfile as sf
import sounddevice as sd
import numpy
assert numpy

def file_writing_thread(*, q, **soundfile_args):
    with sf.SoundFile(**soundfile_args) as file:
        while True:
            data = q.get()
            if data is None:
                break
            file.write(data)

class AudioLib:
    q = queue.Queue()
    stream = None
    recording = False
    previously_recording = False

    def list_input_devices(self):
        inputs = []
        for dev in sd.query_devices():
            if dev['max_input_channels'] > 0:
                inputs.append((dev['name'], dev['index']))
        return inputs

    def default_device(self):
        d = sd.query_devices(kind='input')
        return (d['name'], d['index'])

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if self.recording:
            self.q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                self.q.put(None)
                self.previously_recording = False


    def create_stream(self, device = None, samplerate = None):
        dev = sd.query_devices(device, kind='input')
        if samplerate is None:
            samplerate = dev['default_samplerate']
        if self.stream is not None:
            self.stream.close()
        self.stream = sd.InputStream(samplerate = samplerate, device = device,
                                     channels = dev['max_input_channels'],
                                     callback = self.callback)
        self.stream.start()

    def start_recording(self):
        self.recording = True

        filename = "recording_" + str(datetime.now().strftime('%Y%m%d_%H%M%S')) + ".wav" 
        self.thread = threading.Thread(
                target=file_writing_thread,
                kwargs = dict(
                    file = filename,
                    mode = 'x',
                    samplerate = int(self.stream.samplerate),
                    channels = self.stream.channels,
                    q = self.q,
                    ),
                )
        self.thread.start()

    def stop_recording(self):
        self.recording = False
        self.wait_for_thread()

    def wait_for_thread(self):
        t = threading.Timer(0.01, self._wait_for_thread)
        t.start()

    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()
