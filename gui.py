from tkinter import Tk
## imports
from os import listdir, getcwd

# UI components
from UI_Components.Title import Title
from UI_Components.AppCanvas import AppCanvas

import Data_Classes.Params as p
import Data_Classes.ScenarioData as sd


#### Main UI using Tkinter ###

class MainApplication(Tk):
    def __init__(self):
        super().__init__()

        params = p.Parameters()
        scenario_data = sd.ScenarioData()

        #current working directory
        working_dir = getcwd()
        params.update_parameter("working_dir", working_dir)

        #load already loaded scenarios
        path_to_scenarios = working_dir + "/" + params.get_parameter('output_dir_name')  + "/"
        scenario_files = [pos_json.split(".")[0] for pos_json in listdir(path_to_scenarios) if pos_json.endswith('.json')]
        scenario_data.add_loaded_scenarios(scenario_files)
 
        self.title("Rapid Sensor Analysis")
        #self.configure(bg=bg_color)

        self.width = Tk.winfo_screenwidth(self)
        self.height = Tk.winfo_screenheight(self)
        self.geometry(f"{self.width}x{self.height}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        

        self.title_label = Title(self, text="Rapid Sensor Analysis")
        self.pw = AppCanvas(self, params, scenario_data)
       

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

