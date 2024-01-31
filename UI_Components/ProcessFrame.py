
from tkinter import Frame

from UI_Components.CompareScenariosFrame import CompareScenariosFrame
from UI_Components.LoadScenario import LoadScenarioData
from UI_Components.LabelROIFrame import LabelROIFrame
from UI_Components.AcclimationDepth import AcclimationDepth

class ProcessFrame(Frame):
    def __init__(self, master, console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params=params
        self.scenario_data = scenario_data
        self.plot_frame = plot_frame
        self.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.load_scenario_data_frame = LoadScenarioData(self, console_frame, self.params, self.scenario_data, self.plot_frame)
        self.label_roi_frame = LabelROIFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame)
        self.acclimation_depth_frame = AcclimationDepth(self, console_frame, self.params)
        self.compare_scenarios_frame = CompareScenariosFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame  )

       