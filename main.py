from controllers import audioLibController
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox

class AudioConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.controller = audioLibController.AudioLibController()

        self.title("Conversor de Audio Analógico a Digital")
        self.geometry("800x600") # Tamaño inicial de la ventana

        # --- Frames principales para las secciones ---
        self.recording_frame = tk.Frame(self, bg="lightgray")
        self.history_frame = tk.Frame(self, bg="lightblue")

        # --- Navegación entre secciones ---
        self.create_navbar()

        # Variables de estado para la grabación
        self.is_recording = False
        self.audio_data = [] # Para almacenar los chunks de audio grabados
        self.stream = None # Para mantener la referencia al stream de sounddevice
        self.record_button = None # Para poder cambiar el texto del botón
        self.sampling_rate_val = 0 # Almacenará la tasa de muestreo numérica
        self.bit_depth_val = 0 # Almacenará la profundidad de bits numérica

        self.show_recording_section()
        self.setup_recording_section()
        #self.setup_history_section()

    def on_rec(self):
        self.controller.start_recording()
        self.record_button['text'] = "Stop"
        self.record_button['command'] = self.on_stop

    def on_stop(self):
        self.controller.stop_recording()
        self.record_button['text'] = "Record"
        self.record_button['command'] = self.on_rec

    def create_navbar(self):
        navbar_frame = tk.Frame(self.master, bd=2, relief="raised")
        navbar_frame.pack(side="top", fill="x")

        btn_record = ttk.Button(navbar_frame, text="Grabar/Convertir", command=self.show_recording_section)
        btn_record.pack(side="left", padx=5, pady=5)

        #btn_history = ttk.Button(navbar_frame, text="Historial", command=self.show_history_section)
        #btn_history.pack(side="left", padx=5, pady=5)

    def show_recording_section(self):
        self.history_frame.pack_forget()
        self.recording_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_recording_section(self):
        section_title = ttk.Label(self.recording_frame, text="Grabación y Conversión de Audio", font=("Helvetica", 16, "bold"))
        section_title.pack(pady=10)

        wave_display_frame = tk.Frame(self.recording_frame, bd=2, relief="groove", height=200, width=600, bg="white")
        wave_display_frame.pack(pady=20, padx=20, fill="x", expand=True)
        wave_display_frame.pack_propagate(False)
        wave_placeholder_label = tk.Label(wave_display_frame, text="*Acá va una imagen de la onda siendo grabada*", fg="gray", bg="white")
        wave_placeholder_label.pack(expand=True)

        controls_frame = tk.Frame(self.recording_frame)
        controls_frame.pack(pady=20)

        sample_rate_label = ttk.Label(controls_frame, text="Tasa de muestreo:")
        sample_rate_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sample_rate_var = tk.StringVar()
        self.sample_rate_var.set("44100 Hz")
        sample_rate_options = ["44100 Hz", "48000 Hz", "96000 Hz", "192000 Hz"]
        sample_rate_menu = ttk.OptionMenu(controls_frame, self.sample_rate_var, self.sample_rate_var.get(), *sample_rate_options,command=self.select_samplerate)
        sample_rate_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        device_label = ttk.Label(controls_frame, text="Dispositivo de Grabación:")
        device_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.device_var = tk.StringVar()
        device_names = self.controller.get_device_names()
        self.device_var.set(device_names[0])
        self.device_menu = ttk.OptionMenu(controls_frame, self.device_var, device_names[0], *device_names,command=self.select_device)
        self.device_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.record_button = ttk.Button(self.recording_frame, text="Grabar", command=self.toggle_recording)
        self.record_button.pack(pady=20)

    def toggle_recording(self):
        if not self.is_recording:
            self.on_rec()
            self.is_recording = True
        else:
            self.on_stop()
            self.is_recording = False

    def select_device(self,value):
        self.controller.select_device(value)

    def select_samplerate(self,value):
        num = int(value.split()[0])
        if self.controller.select_samplerate(num):
            messagebox.showerror("Error", "El microfono no soporta la tasa de muestreo " + num + " Hz")

       

def main():
    try:
        app = AudioConverterApp()
        app.mainloop()
    except Exception as e:
        print("Error al iniciar la aplicación:", e)

if __name__ == "__main__":
    main()