import tkinter as tk
from tkinter import ttk # ttk para widgets más modernos
import sounddevice as sd
import numpy as np
import wavio
import datetime

class AudioConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Conversor de Audio Analógico a Digital")
        master.geometry("800x600") # Tamaño inicial de la ventana

        # --- Frames principales para las secciones ---
        self.recording_frame = tk.Frame(master, bg="lightgray")
        self.history_frame = tk.Frame(master, bg="lightblue")

        # --- Navegación entre secciones ---
        self.create_navbar()

        # Variables de estado para la grabación
        self.is_recording = False
        self.audio_data = [] # Para almacenar los chunks de audio grabados
        self.stream = None # Para mantener la referencia al stream de sounddevice
        self.record_button = None # Para poder cambiar el texto del botón
        self.sampling_rate_val = 0 # Almacenará la tasa de muestreo numérica
        self.bit_depth_val = 0 # Almacenará la profundidad de bits numérica

        # Mostrar la primera sección por defecto
        self.show_recording_section()

        # --- Contenido de la sección de Grabación/Conversión ---
        self.setup_recording_section()

        # --- Contenido de la sección de Historial ---
        self.setup_history_section()

    def create_navbar(self):
        """Crea la barra de navegación para cambiar entre secciones."""
        navbar_frame = tk.Frame(self.master, bd=2, relief="raised")
        navbar_frame.pack(side="top", fill="x")

        btn_record = ttk.Button(navbar_frame, text="Grabar/Convertir", command=self.show_recording_section)
        btn_record.pack(side="left", padx=5, pady=5)

        btn_history = ttk.Button(navbar_frame, text="Historial", command=self.show_history_section)
        btn_history.pack(side="left", padx=5, pady=5)

    def show_recording_section(self):
        """Muestra la sección de Grabación/Conversión y oculta las otras."""
        self.history_frame.pack_forget() # Oculta el historial si está visible
        self.recording_frame.pack(fill="both", expand=True, padx=10, pady=10) # Muestra la sección de grabación

    def show_history_section(self):
        """Muestra la sección de Historial y oculta las otras."""
        self.recording_frame.pack_forget() # Oculta la grabación si está visible
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=10) # Muestra la sección de historial

    def setup_recording_section(self):
        """Configura los elementos de la sección de Grabación/Conversión."""
        section_title = ttk.Label(self.recording_frame, text="Grabación y Conversión de Audio", font=("Helvetica", 16, "bold"))
        section_title.pack(pady=10)

        # Contenedor para la imagen de la onda
        wave_display_frame = tk.Frame(self.recording_frame, bd=2, relief="groove", height=200, width=600, bg="white")
        wave_display_frame.pack(pady=20, padx=20, fill="x", expand=True)
        wave_display_frame.pack_propagate(False)
        wave_placeholder_label = tk.Label(wave_display_frame, text="*Acá va una imagen de la onda siendo grabada*", fg="gray", bg="white")
        wave_placeholder_label.pack(expand=True)

        # Frame para los controles de muestreo y bits
        controls_frame = tk.Frame(self.recording_frame)
        controls_frame.pack(pady=20)

        # Tasa de muestreo
        sample_rate_label = ttk.Label(controls_frame, text="Tasa de muestreo:")
        sample_rate_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sample_rate_var = tk.StringVar(self.master)
        self.sample_rate_var.set("44100 Hz")
        sample_rate_options = ["8000 Hz", "16000 Hz", "22050 Hz", "44100 Hz", "48000 Hz", "96000 Hz"]
        sample_rate_menu = ttk.OptionMenu(controls_frame, self.sample_rate_var, self.sample_rate_var.get(), *sample_rate_options)
        sample_rate_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Bits de grabación (Profundidad de bits/Cuantización)
        bit_depth_label = ttk.Label(controls_frame, text="Bits de grabación:")
        bit_depth_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.bit_depth_var = tk.StringVar(self.master)
        self.bit_depth_var.set("16 bits")
        bit_depth_options = ["8 bits", "16 bits", "24 bits", "32 bits"]
        bit_depth_menu = ttk.OptionMenu(controls_frame, self.bit_depth_var, self.bit_depth_var.get(), *bit_depth_options)
        bit_depth_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Dispositivo de Grabación
        device_label = ttk.Label(controls_frame, text="Dispositivo de Grabación:")
        device_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.device_var = tk.StringVar(self.master)
        # self.device_var.set("Default") # Ya no establecemos un valor por defecto fijo aquí
        # device_options = ["Default", "Micrófono USB", "Entrada de línea"] # ¡Esta línea se va!

        # Creamos el OptionMenu y luego lo actualizamos con los dispositivos reales
        self.device_menu = ttk.OptionMenu(controls_frame, self.device_var, "", *[]) # Inicialmente vacío
        self.device_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Llamar a una función para poblar la lista de dispositivos
        self.populate_audio_devices()

        # Botón Grabar
        self.record_button = ttk.Button(self.recording_frame, text="Grabar", command=self.toggle_recording)
        self.record_button.pack(pady=20)

    def setup_history_section(self):
        """Configura los elementos de la sección de Historial."""
        section_title = ttk.Label(self.history_frame, text="Historial de Grabaciones", font=("Helvetica", 16, "bold"))
        section_title.pack(pady=10)

        # Encabezados de la tabla (Nombre, Fecha, Peso (Kb))
        header_frame = tk.Frame(self.history_frame, bd=1, relief="solid")
        header_frame.pack(fill="x", padx=20)
        ttk.Label(header_frame, text="Nombre", font=("Helvetica", 10, "bold")).pack(side="left", expand=True)
        ttk.Label(header_frame, text="Fecha", font=("Helvetica", 10, "bold")).pack(side="left", expand=True)
        ttk.Label(header_frame, text="Peso (Kb)", font=("Helvetica", 10, "bold")).pack(side="left", expand=True)

        # Área de desplazamiento para la lista de elementos del historial
        history_canvas = tk.Canvas(self.history_frame, borderwidth=0, background="#ffffff")
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=history_canvas.yview)
        self.history_inner_frame = tk.Frame(history_canvas, background="#ffffff")

        history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor="nw")
        history_canvas.configure(yscrollcommand=history_scrollbar.set)

        history_scrollbar.pack(side="right", fill="y", padx=(0, 20))
        history_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)

        # Datos de ejemplo para el historial (reemplazar con datos reales de MongoDB)
        self.add_history_entry("Grabacion_001.wav", "2025-06-19", "1250")
        self.add_history_entry("Conferencia.mp3", "2025-06-18", "5430")
        self.add_history_entry("Prueba_Voz.wav", "2025-06-17", "780")
        for i in range(10): # Más entradas para probar el scroll
            self.add_history_entry(f"Audio_{i+1}.wav", f"2025-06-{16-i}", f"{500+i*10}")

        # Configurar el scrollbar para que se actualice con el contenido
        self.history_inner_frame.bind("<Configure>", lambda e: history_canvas.configure(scrollregion = history_canvas.bbox("all")))

    def populate_audio_devices(self):
        """Obtiene la lista de dispositivos de audio de entrada y actualiza el OptionMenu."""
        try:
            # Obtener todos los dispositivos
            devices = sd.query_devices()
            # Filtrar solo los dispositivos de entrada (micrófonos)
            input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]

            if not input_devices:
                # Si no se encuentra ningún dispositivo de entrada, usar un placeholder
                input_devices = ["No se encontraron dispositivos de entrada"]
                self.device_var.set(input_devices[0])
            else:
                # Establecer el primer dispositivo como seleccionado por defecto
                self.device_var.set(input_devices[0])

            # Eliminar opciones antiguas del menú
            self.device_menu['menu'].delete(0, 'end')

            # Añadir las nuevas opciones al menú
            for device_name in input_devices:
                self.device_menu['menu'].add_command(label=device_name,
                                                   command=tk._setit(self.device_var, device_name))

        except Exception as e:
            # Manejo de errores si sounddevice no puede acceder a los dispositivos
            print(f"Error al listar dispositivos de audio: {e}")
            self.device_var.set("Error al cargar dispositivos")
            self.device_menu['menu'].delete(0, 'end') # Limpia el menú
            self.device_menu['menu'].add_command(label="Error al cargar dispositivos",
                                               command=tk._setit(self.device_var, "Error al cargar dispositivos"))

    def add_history_entry(self, name, date, size_kb):
        """Agrega una entrada al historial de grabaciones."""
        entry_frame = tk.Frame(self.history_inner_frame, bd=1, relief="raised", padx=5, pady=5)
        entry_frame.pack(fill="x", pady=2, padx=5)

        ttk.Label(entry_frame, text=name).pack(side="left", expand=True)
        ttk.Label(entry_frame, text=date).pack(side="left", expand=True)
        ttk.Label(entry_frame, text=size_kb).pack(side="left", expand=True)

        # Aquí podrías añadir botones para "Reproducir", "Exportar", "Eliminar" por cada entrada si lo deseas

    # --- Funcionalidades (por ahora solo placeholders) ---
    def toggle_recording(self):
        """Alterna entre iniciar y detener la grabación."""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Inicia la grabación de audio."""
        try:
            # Obtener los valores de los selectores
            selected_sample_rate = self.sample_rate_var.get().split(' ')[0]
            selected_bit_depth = self.bit_depth_var.get().split(' ')[0]
            selected_device_name = self.device_var.get()

            self.sampling_rate_val = int(selected_sample_rate)
            self.bit_depth_val = int(selected_bit_depth)

            # Encontrar el índice del dispositivo seleccionado
            device_info = sd.query_devices(selected_device_name, 'input')
            device_index = device_info['index'] if device_info else None

            if device_index is None:
                tk.messagebox.showerror("Error de Grabación", "No se pudo encontrar el dispositivo de grabación seleccionado.")
                return

            # Limpiar datos de audio anteriores
            self.audio_data = []

            # Callback para sounddevice (se ejecuta cuando hay datos de audio)
            def callback(indata, frames, time, status):
                if status:
                    print(status)
                self.audio_data.append(indata.copy())

            # Iniciar el stream de sounddevice
            # dtype mapea los bits a un formato de numpy compatible
            dtype = f'int{self.bit_depth_val}'
            if self.bit_depth_val == 32: # float32 es común para 32 bits en audio
                dtype = 'float32'

            self.stream = sd.InputStream(
                samplerate=self.sampling_rate_val,
                device=device_index,
                channels=1, # Por ahora, un solo canal (mono)
                dtype=dtype,
                callback=callback
            )
            self.stream.start()

            self.is_recording = True
            self.record_button.config(text="Detener Grabación", command=self.toggle_recording)
            print("Grabación iniciada...")

        except Exception as e:
            tk.messagebox.showerror("Error de Grabación", f"No se pudo iniciar la grabación: {e}")
            self.is_recording = False
            self.record_button.config(text="Grabar", command=self.toggle_recording)


    def _stop_recording(self):
        """Detiene la grabación de audio y guarda el archivo."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_recording = False
            self.record_button.config(text="Grabar", command=self.toggle_recording)
            print("Grabación detenida.")

            if self.audio_data:
                # Concatenar todos los chunks de audio grabados
                # np.concatenate funciona mejor con una lista de arrays
                recorded_audio = np.concatenate(self.audio_data, axis=0)

                # Normalizar si es float32 (para asegurar que el rango sea -1 a 1)
                if self.bit_depth_val == 32:
                    # En sounddevice, si dtype es float32, los datos ya vienen en el rango -1 a 1.
                    # No es necesario una normalización adicional aquí a menos que veas clipping.
                    # Asegurarse de que el array tenga la forma correcta para wavio (canales al final)
                    # En este caso, channels=1, así que la forma es (samples, 1)
                    pass
                else:
                    # Para int, asegurarse que los datos estén en el rango correcto.
                    # sounddevice ya devuelve los int en el rango correcto.
                    # Para wavio, si es int16, solo necesitas el array.
                    pass


                # Guardar el archivo WAV
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"grabacion_{timestamp}.wav"
                try:
                    # wavio.write espera (data, rate, sampwidth)
                    # sampwidth es el tamaño de la muestra en bytes (8 bits = 1 byte, 16 bits = 2 bytes, etc.)
                    # Los datos deben ser de la forma (samples, channels) o (samples,) si es mono
                    if recorded_audio.ndim == 1: # Si es mono y la forma es (samples,)
                        wavio.write(filename, recorded_audio, self.sampling_rate_val, sampwidth=self.bit_depth_val // 8)
                    else: # Si ya tiene la forma (samples, channels)
                        wavio.write(filename, recorded_audio, self.sampling_rate_val, sampwidth=self.bit_depth_val // 8)

                    tk.messagebox.showinfo("Grabación Completada", f"Audio guardado como: {filename}")
                    print(f"Audio guardado como: {filename}")

                    # Aquí podrías añadir el archivo al historial
                    # self.add_history_entry(filename, pd.to_datetime('now').strftime('%Y-%m-%d'), "calcula_peso_kb")

                except Exception as e:
                    tk.messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo de audio: {e}")
            else:
                tk.messagebox.showwarning("Grabación Vacía", "No se grabó ningún audio.")

    # Más funciones para cargar audio, procesar, exportar, etc.

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()