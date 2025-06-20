from lib import audioLib
import tkinter as tk
from tkinter import ttk

class mainApp(tk.Tk):
    al = None
    def __init__(self, audiolib):
        super().__init__()
        self.al = audiolib

        self.title = "Test App"
        f = ttk.Frame()

        self.rec_button = ttk.Button(f)
        self.rec_button['text'] = "Record"
        self.rec_button['command'] = self.on_rec
        self.rec_button.pack(side='left', padx = 10, pady=10)
        f.pack(expand = True, padx=10, pady=10)

    def on_rec(self):
        self.al.start_recording()
        self.rec_button['text'] = "Stop"
        self.rec_button['command'] = self.on_stop

    def on_stop(self):
        self.al.stop_recording()
        self.rec_button['text'] = "Record"
        self.rec_button['command'] = self.on_rec

def main():
    al = audioLib.AudioLib()
    print(al.list_input_devices())
    print(al.default_device())
    al.create_stream(al.default_device()[1])
    app = mainApp(al)
    app.mainloop()

if __name__ == "__main__":
    main()

