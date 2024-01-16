from tkinter import Label,LabelFrame,Button,Frame
from tkinter.ttk import Combobox

from API import rapid_api as api

class CompareScenariosFrame(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data = scenario_data
        self.console_frame = console_frame
        self.plot_frame = plot_frame
        self.configure(text = "Plot Scenario Results",)
        self.grid(row=2, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(2, weight=1)

        self.loaded_scenarios_A = Label(self, text = "Scenario : ")
        self.loaded_scenarios_A.grid(row=2, column=0, columnspan=1, sticky='e')
        self.scenario_A_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_A_combo.grid(row=2, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)

        self.loaded_scenarios_B = Label(self, text = "Compare with : ")
        self.loaded_scenarios_B.grid(row=3, column=0, columnspan=1, sticky='e')
        self.scenario_B_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_B_combo.grid(row=3, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)

        for item in self.scenario_data.get_loaded_scenarios():
            s_data = api.read_scenario_from_json_file(self.params, item)
            for r in s_data["runs"]:
                #at least 1 run is fully labelled
                if(r["labeled"] == True):
                    self.scenario_A_combo['values'] = (*self.scenario_A_combo['values'], item)
                    self.scenario_B_combo['values'] = (*self.scenario_B_combo['values'], item)

            #if("labeled" in s_data):

                #if scenario fully labelled
            #    if(s_data["labeled"] == True):
            #        self.scenario_A_combo['values'] = (*self.scenario_A_combo['values'], item)
            #        self.scenario_B_combo['values'] = (*self.scenario_B_combo['values'], item)

            
                    
        
        self.scenario_A_combo.bind("<<ComboboxSelected>>", self.on_first_scenario_select)
        self.scenario_B_combo.bind("<<ComboboxSelected>>", self.on_second_scenario_select)

        # future
        self.scenarios_to_compare = []
        self.first_scenario_name = ""
        self.second_scenario_name = ""

        self.compare_button_frame = Frame(self)
        self.compare_button_frame.grid(row=5, column=0, columnspan=2)
        self.compare_scenarios_box_plot_btn = Button(self.compare_button_frame,text='Box Plots', command=self.compare_scenarios_with_box_plots)
        self.compare_scenarios_box_plot_btn.grid(row=5, column=0,sticky='ws',pady=5 )
        self.compare_scenarios_pressure_rpc_btn = Button(self.compare_button_frame,text='Pressure / PRC Plots', command=self.compare_scenarios_pressure_and_rpc)
        self.compare_scenarios_pressure_rpc_btn.grid(row=5, column=1,sticky='ws',pady=5 )
        self.compare_scenarios_mean_diff_btn = Button(self.compare_button_frame,text='Mean / Diff', command=self.compare_scenarios_mean_diff)
        self.compare_scenarios_mean_diff_btn.configure(state="disabled")
        self.compare_scenarios_mean_diff_btn.grid(row=5, column=2,sticky='ws',pady=5 )

        self.set_ref_on_plot_frame(self)

    def set_ref_on_plot_frame(self, ref):
        self.plot_frame.set_ref_to_compare_frame(ref)

    def compare_scenarios_mean_diff(self):
        if(self.second_scenario_name and self.first_scenario_name):
            self.plot_frame.table_3_frame.grid_remove()
            scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
            scenarios = api.get_scenarios_to_compare(scenarios, self.params)
            plot = api.create_mean_diff_plots(scenarios, self.plot_frame.fig)
            self.plot_frame.fig.canvas.draw()

    def compare_scenarios_pressure_and_rpc(self):
        self.plot_frame.table_3_frame.grid_remove()
        scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
        scenarios = api.get_scenarios_to_compare(scenarios, self.params)
        plot = api.create_fig_7_pressure_and_rpc_plots(scenarios, self.plot_frame.fig)
        self.plot_frame.fig.canvas.draw()


    def compare_scenarios_with_box_plots(self):
        self.plot_frame.table_3_frame.grid_remove()
        scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
        scenarios = api.get_scenarios_to_compare(scenarios, self.params)
        plot = api.create_fig_6_box_plots(scenarios, self.plot_frame.fig)
        self.plot_frame.fig.canvas.draw()

    def on_first_scenario_select(self, event):
        first_selected_scenario = self.scenario_A_combo.get()
        self.first_scenario_name  = first_selected_scenario
        self.scenarios_to_compare.append(first_selected_scenario)
    
    def on_second_scenario_select(self, event):
        #note disable this out until first is selected
        second_selected_scenario = self.scenario_B_combo.get()
        self.second_scenario_name  = second_selected_scenario
        self.scenarios_to_compare.append(second_selected_scenario)
        if(len(self.scenarios_to_compare) > 1):
            self.compare_scenarios_mean_diff_btn.configure(state="active")