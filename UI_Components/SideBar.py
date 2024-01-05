from tkinter import PanedWindow

from UI_Components.ProcessFrame import ProcessFrame

class SideBar(PanedWindow):
     def __init__(self, master, console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data = scenario_data
        self.plot_frame = plot_frame
        self.configure(orient="vertical",  sashwidth = 10)
        self.grid(row=0, column=0,rowspan=2,columnspan=1, sticky='news')
        self.grid_rowconfigure(0, weight=1)
        self.process_frame = ProcessFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame)
        self.console_frame = console_frame
        self.add(self.process_frame)
        self.add(self.console_frame)