from lib.audioLib import AudioLib
from repository.audioRepository import AudioRepository

class AudioLibController:
    def __init__(self):
        self.audio_lib = AudioLib()
        self.audio_repository = AudioRepository()

    def get_devices(self):
        return self.audio_lib.list_input_devices()
    
    def get_device_names(self):
     return [d[0] for d in self.get_devices()]      
    
    def select_device(self, device_name):
        devices = self.get_devices()
        for d in devices:
            if d[0] == device_name:
                self.audio_lib.select_device(d)
                break

    def select_samplerate(self,samplerate):
        return self.audio_lib.select_samplerate(samplerate) 

    def start_recording(self):
        self.audio_lib.start_recording()

    def stop_recording(self):
        resp = self.audio_lib.stop_recording()
        self.guardar_audio(resp)

    def guardar_audio(self,resp):
        self.audio_repository.guardar_audio(resp[0],resp[1],resp[2])

    def listar_audios(self):
        return self.audio_repository.listar_audios()    
        
        

