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
        self.setup_history_section()

    def on_rec(self):
        self.controller.start_recording()
        self.record_button['text'] = "Stop"
        self.record_button['command'] = self.on_stop

    def on_stop(self):
        self.controller.stop_recording()
        self.record_button['text'] = "Record"
        self.record_button['command'] = self.on_rec
        #Recorrer listado de audios
        listado_audios = self.listar_audios()
        for widget in self.history_inner_frame.winfo_children():
            widget.destroy()
        for i in listado_audios:
            print(i)
            self.add_history_entry(
                i["nombre"].split("\\")[-1],
                str(i["metadata"]["fecha_guardado"])[:16],
                i["metadata"]["dispositivo_de_grabacion"],
                i["metadata"]["size_kb"]             
            )


    def create_navbar(self):
        navbar_frame = tk.Frame(self.master, bd=2, relief="raised")
        navbar_frame.pack(side="top", fill="x")

        btn_record = ttk.Button(navbar_frame, text="Grabar y Convertir", command=self.show_recording_section)
        btn_record.pack(side="left", padx=5, pady=5)

        btn_history = ttk.Button(navbar_frame, text="Historial", command=self.show_history_section)
        btn_history.pack(side="left", padx=5, pady=5)

    def show_recording_section(self):
        self.history_frame.pack_forget()
        self.recording_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def show_history_section(self):
        self.recording_frame.pack_forget()
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_recording_section(self):
        section_title = ttk.Label(self.recording_frame, text="Grabación y Conversión de Audio", font=("Helvetica", 16, "bold"))
        section_title.pack(pady=10)

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

    def setup_history_section(self):
        """Configura los elementos de la sección de Historial."""
        section_title = ttk.Label(self.history_frame, text="Historial de Grabaciones", font=("Helvetica", 16, "bold"))
        section_title.pack(pady=10)

        header_frame = tk.Frame(self.history_frame, bd=1, relief="solid", background="white")
        header_frame.pack(fill="x", padx=20)
        ttk.Label(header_frame, text="Nombre", font=("Helvetica", 10, "bold"), width=25, anchor="w").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(header_frame, text="Fecha", font=("Helvetica", 10, "bold"), width=25, anchor="w").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(header_frame, text="Dispositivo Grabacion", font=("Helvetica", 10, "bold"), width=35, anchor="w").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Label(header_frame, text="Peso (Kb)", font=("Helvetica", 10, "bold"), width=10, anchor="w").grid(row=0, column=3, sticky="w", padx=5)



        history_canvas = tk.Canvas(self.history_frame, borderwidth=0, background="#ffffff")
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=history_canvas.yview)
        self.history_inner_frame = tk.Frame(history_canvas, background="#ffffff")

        history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor="nw")
        history_canvas.configure(yscrollcommand=history_scrollbar.set)

        history_scrollbar.pack(side="right", fill="y", padx=(0, 20))
        history_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)

    
        #Recorrer listado de audios
        listado_audios = self.listar_audios()
        for widget in self.history_inner_frame.winfo_children():
            widget.destroy()
        for i in listado_audios:
            print(i)
            self.add_history_entry(
                i["nombre"].split("\\")[-1],
                str(i["metadata"]["fecha_guardado"])[:16],
                i["metadata"]["dispositivo_de_grabacion"],
                i["metadata"]["size_kb"]             
            )
        self.history_inner_frame.bind("<Configure>", lambda e: history_canvas.configure(scrollregion = history_canvas.bbox("all")))

    def add_history_entry(self, name, date, device, size_kb):
        row_index = self.history_inner_frame.grid_size()[1]

        # Contenedor para la fila completa
        row_frame = tk.Frame(self.history_inner_frame, bg="white")
        row_frame.grid(row=row_index, column=0, columnspan=4, sticky="nsew")


        def on_row_click(event):
            nombre = name  # ya lo tenés definido al crear la fila
            exito = self.controller.obtener_audio_por_nombre(nombre)

            if exito:
                messagebox.showinfo("Audio descargado", f"El archivo '{nombre}' fue descargado correctamente'")
            else:
                messagebox.showerror("Error", f"No se pudo encontrar el archivo '{nombre}' en la base de datos.")


        # Asociar evento click al contenedor de la fila
        row_frame.bind("<Button-1>", on_row_click)

        # Crear labels dentro del frame de fila
        ttk.Label(row_frame, text=name, width=25, anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(row_frame, text=date, width=25, anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(row_frame, text=device, width=35, anchor="w").grid(row=0, column=2, sticky="w", padx=10, pady=2)
        ttk.Label(row_frame, text=size_kb, width=10, anchor="w").grid(row=0, column=3, sticky="w", padx=5, pady=2)

        # También podés hacer que los labels propaguen el clic
        for child in row_frame.winfo_children():
            child.bind("<Button-1>", on_row_click)

          

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

    def listar_audios(self):
        return self.controller.listar_audios()        


def main():
    try:
        app = AudioConverterApp()
        app.mainloop()
    except Exception as e:
        print("Error al iniciar la aplicación:", e)

if __name__ == "__main__":
    main()