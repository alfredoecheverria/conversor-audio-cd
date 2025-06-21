from datetime import datetime
import threading
import queue
import sys
import os

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
    selected_device = None
    selected_samplerate = None
    max_channels = None
    current_filename = ""

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

    def select_device(self, device):
        self.selected_device = device[1]
        self.max_channels = sd.query_devices(device[1], kind='input')['max_input_channels']

    def select_samplerate(self, samplerate):
        if sd.check_input_settings(device = self.selected_device, samplerate = samplerate): 
            self.selected_samplerate = int(samplerate)
            return True
        else:
            return False

    def create_stream(self):
        if self.selected_device is None:
            self.selected_device = self.default_device()[1]
        if self.selected_samplerate is None:
            dev = sd.query_devices(self.selected_device, kind='input')
            self.selected_samplerate = dev['default_samplerate']
        if self.stream is not None:
            self.stream.close()
        self.stream = sd.InputStream(samplerate = self.selected_samplerate, device = self.selected_device,
                                     channels = self.max_channels, callback = self.callback)
        self.stream.start()

    def start_recording(self):
        if self.stream is None:
            self.create_stream()
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
        self.current_filename = filename

    def stop_recording(self):
        self.recording = False
        self.wait_for_thread()
        return (os.getcwd() + self.current_filename, str(int(os.stat(self.current_filename).st_size / 1024)) + "Kb", 
              sd.query_devices(self.selected_device)['name']) 

    def wait_for_thread(self):
        t = threading.Timer(0.01, self._wait_for_thread)
        t.start()

    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()
