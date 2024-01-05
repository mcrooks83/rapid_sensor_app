
from tkinter import PanedWindow

from UI_Components.PlotFrame import PlotFrame
from UI_Components.LeftFrame import LeftFrame
from UI_Components.Console import ConsoleFrame as console

class AppCanvas(PanedWindow):
    def __init__(self, master, params, scenario_data,  *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        console_frame = console(master)
        self.scenario_data = scenario_data
        self.config(orient="horizontal",  sashwidth = 10)
        self.grid(row=1, column=0,rowspan=1,columnspan=1, sticky='news',padx=3,pady=3)
        self.plot_frame = PlotFrame(self, console_frame, self.params, self.scenario_data)
        self.left_frame = LeftFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame)
 
        self.add(self.left_frame)
        self.add(self.plot_frame)  