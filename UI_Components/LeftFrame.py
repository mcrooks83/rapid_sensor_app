from tkinter import Frame

from UI_Components.ButtonFrame import ButtonFrame
from UI_Components.SideBar import SideBar

class LeftFrame(Frame):
    def __init__(self, master, console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params=params
        self.scenario_data = scenario_data
        self.plot_frame = plot_frame
        self.console_frame = console_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.sidebar = SideBar(self, self.console_frame, self.params, self.scenario_data, self.plot_frame)
        self.button_frame = ButtonFrame(self, self.console_frame, self.params, self.scenario_data)