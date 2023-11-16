from tkinter import Label, CENTER

class Title(Label):
    def __init__(self, master, text, *args, **kwargs):
        super().__init__(master, width=60, height=1, bg='black', fg="#ffffff", text="Rapid Sensor Analysis",  font=("Hallo Sans", 20, "bold"), anchor=CENTER, *args, **kwargs)
        self.grid(row=0, column=0, columnspan=1, sticky='nsew')
