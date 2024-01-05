#tkinter
from tkinter import Button,Frame
from Functions.read_me import read_me_text, readme_heading_text

class ButtonFrame(Frame):
    def __init__(self, master, console_frame, params, scenario_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data = scenario_data
        self.console_frame = console_frame
        self.grid(row=2, column=0,rowspan=1,columnspan=1, sticky='nsew') 
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.clear_console_button =  Button(self,text='Clear console',command=self.clear_console)
        self.clear_console_button.grid(row=0, column=1, columnspan=1, sticky='ew',padx=5,pady=5)
        self.readme_button = Button(self, text='   Manual    ',command=self.read_me)
        self.readme_button.grid(row=0, column=0, columnspan=1, sticky='ew',padx=5,pady=5)
    
    def clear_console(self):
        self.console_frame.clear_console()

    def read_me(self):
        self.console_frame.configure_state("normal")
        self.console_frame.insert_text(readme_heading_text)
        self.console_frame.tag_config('manual_mess', foreground='green', underline=1)
        self.console_frame.insert_text(read_me_text)
        self.console_frame.configure_state(state ='disabled')