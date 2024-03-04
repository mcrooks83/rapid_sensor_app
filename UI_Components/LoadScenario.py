from tkinter import E,W,S,N, IntVar, Toplevel,BOTH, INSERT,END,Tk,PanedWindow,Label,LabelFrame,CENTER,Button,Frame,Entry,RIGHT,StringVar,Radiobutton,Checkbutton,Text,Scrollbar, Listbox
from tkinter import filedialog as fd
from tkinter.ttk import Combobox, Progressbar

import queue
import multiprocessing


from API import rapid_api as api

class LoadScenarioData(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data =scenario_data
        self.plot_frame = plot_frame
        self.console_frame = console_frame
        self.configure(text = "Import Scenario",)
        self.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(0, weight=1)
        self.data_dir = Label(self, text = "Sensor Version : ")
        self.data_dir.grid(row=0, column=0, )
        self.sensor_version_var = IntVar()
        self.sensor_version_var.set(params.get_parameter("sensor_version"))
        self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " " + str(params.get_parameter("fs")) + " Hz" + '\n') 
        self.v1_radio_button = Radiobutton(self, text="v1", value=1, variable = self.sensor_version_var, command=self.update_sensor_version)
        self.v1_radio_button.grid(row=0,column=1,pady=5, sticky="w")
        self.v1_radio_button = Radiobutton(self, text="v2", value=2, variable = self.sensor_version_var, command=self.update_sensor_version)
        self.v1_radio_button.grid(row=0,column=1,pady=5, )
        self.data_dir = Label(self, text = "Data directory : ")
        self.data_dir.grid(row=1, column=0, columnspan=1, sticky='e')
        self.open_button = Button(self,text='Scenario data directory',command=self.select_dir)
        self.open_button.grid(row=1, column=1, columnspan=1, sticky='w',pady=5)
        self.step1button_frame = Frame(self)
        self.step1button_frame.grid(row=1, column=3,columnspan=1, sticky='e')
        self.step1run_button = Button(self.step1button_frame,text='Import Scenario ',command=self.load_scenario)
        self.step1run_button.grid(row=0, column=1, columnspan=1, sticky='ew',padx=5,pady=5)
        self.step1run_button.configure(state="disabled")
        self.loaded_scenarios = Label(self, text = "Scenarios : ")
        self.loaded_scenarios.grid(row=2, column=0, columnspan=1, sticky='e')
        self.scenario_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_combo.grid(row=2, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)
        self.selected_scenario = Label(self, text="")
        self.selected_scenario.grid(row=2, column=3,columnspan=1, sticky='nw',padx=5)
        self.loaded_runs = Label(self, text = "Runs : ")
        self.loaded_runs.grid(row=4, column=0, columnspan=1, sticky='e')
        self.run_combo =  Combobox(self,  width=20,state = "readonly")
        self.run_combo.grid(row=4, column=1, columnspan=2, sticky='w',padx=5,pady=5)
        self.selected_run = Label(self, text="")
        self.selected_run.grid(row=4, column=3,columnspan=1, sticky='nw',padx=5)

        for item in self.scenario_data.get_loaded_scenarios():
            self.scenario_combo['values'] = (*self.scenario_combo['values'], item)

        self.scenario_combo.bind("<<ComboboxSelected>>", self.on_scenario_combo_select)
        self.run_combo.bind("<<ComboboxSelected>>", self.on_run_combo_select)
        self.progress_bar_frame = Frame(self)
        self.progress_bar_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar_frame.grid_rowconfigure(7, weight=1)
        self.progress_bar_frame.grid(row=7, column=0,columnspan=7, sticky='ew')
        self.pbar_ind = Progressbar(self.progress_bar_frame, orient="horizontal",   mode="indeterminate", )
        self.pbar_ind.grid(row=7, column=0, columnspan=7, sticky="news") #sticky="ewns")
        self.blank = Frame(self.progress_bar_frame)
        self.blank.grid(row=7, column=0, columnspan=7, sticky="news")
        self.result_queue = multiprocessing.Queue()
        self.deployment_done_queue = multiprocessing.Queue()

    def update_sensor_version(self):
        self.step1run_button.configure(state="disabled")
        if(self.sensor_version_var.get() == 1):
            self.console_frame.clear_console()
            self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " 100 Hz" '\n') 
            self.params.update_parameter("sensor_version", self.sensor_version_var.get())
            self.params.update_parameter("fs", 2048)
            self.params.update_parameter("fs_p", 100)
            self.params.update_parameter("packet_length", 11)
        elif(self.sensor_version_var.get() == 2):
            self.console_frame.clear_console()
            self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " 2000 Hz" '\n') 
            self.params.update_parameter("sensor_version", self.sensor_version_var.get())
            self.params.update_parameter("fs", 100)
            self.params.update_parameter("fs_p", 100)
            self.params.update_parameter("packet_length", 29)

    def on_run_combo_select(self, event):
        selected_run = self.run_combo.get()
        self.selected_run.config(text={selected_run})
        self.scenario_data.set_selected_run(selected_run)
        scenario_data = self.scenario_data.get_scenario_data()
        self.plot_frame.fig_combo.configure(values=())
        self.plot_frame.fig_combo.set("")
        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for d in r["deployments"]:
                    add_label = "(not labeled)"
                    if d['is_faulty']:
                        add_label="(faulty)"
                    elif d['labeled']:
                        add_label= "(labeled)"
                    dep = d['name'] + " " + add_label
                    self.plot_frame.fig_combo['values'] = (*self.plot_frame.fig_combo['values'], dep)

    def on_scenario_combo_select(self, event):
        selected_scenario = self.scenario_combo.get()
        print("Loading scenario", flush=True)
        self.selected_scenario.config(text={selected_scenario})
        s_data = api.read_scenario_from_json_file(self.params, selected_scenario)
        self.scenario_data.add_scenario_data(s_data)
        self.run_combo.configure(values=())
        self.run_combo.set("")

        for r in s_data["runs"]:
            print("loaded runs in scenario", r["name"])
            self.run_combo['values'] = (*self.run_combo['values'], r['name'])
        self.console_frame.insert_text("Loaded " + s_data["name"] + "" '\n') 

    def start_loading_progress(self):
        print("progressing...")
        self.pbar_ind.start()

    def stop_loading_progress(self):
        print("stop progress")
        self.pbar_ind.stop()
        self.pbar_ind.config(mode="indeterminate")

    def check_process_result(self, process, result_queue):
            try:
                data = result_queue.get(block=False)

                if("run_status" in data):
                    self.console_frame.insert_text(f"processing {data['run_status']['run_no']} of {data['run_status']['runs']} runs ({data['run_status']['run_name']})..." + '\n') 
                    self.after(1, self.check_process_result, process, self.result_queue)

                elif("deployment_status" in data):
                    self.console_frame.insert_text(f"   processing {data['deployment_status']['deployment_no']} of {data['deployment_status']['deployments']} deployments ({data['deployment_status']['deployment_name']})..." + '\n') 
                    self.after(1, self.check_process_result, process, self.result_queue)

                elif "d" in data:
                    print("processed deployment", data["d"])
                    self.console_frame.insert_text("    processed deployment " + data["d"] + '\n') 
                    self.after(1, self.check_process_result, process, self.result_queue)
                else:
                    scenario_data = data
                    print("loading completed")
                    self.console_frame.insert_text('\n' + scenario_data["name"] + " loading complete" '\n') 
                    self.stop_loading_progress()
                    self.pbar_ind.lower()

                    if scenario_data:
                        print("writing data")
                        self.console_frame.insert_text("Saving " + scenario_data["name"] + " please wait..." '\n') 
                        write_data = api.write_scenario_to_json_file(scenario_data, self.params)
                        if(write_data):
                            self.scenario_data.add_loaded_scenario(scenario_data["name"])
                            print("scenario written succcesfully")
                            self.console_frame.insert_text("Scenario " + scenario_data["name"] + " saved succesfully" '\n') 
                        if scenario_data["name"] not in self.scenario_combo['values']:
                            self.scenario_combo['values'] =  (*self.scenario_combo['values'], scenario_data["name"])
                
            except queue.Empty:
                self.after(1, self.check_process_result, process, self.result_queue)

    def load_scenario(self):
        self.console_frame.clear_console()
        print("loading scenario")
        self.pbar_ind.tkraise()
        self.pbar_ind.start()
        self.console_frame.insert_text('\n' + "Loading scenario, please wait ..." + '\n\n') 
        sensor_version = self.sensor_version_var.get()
        print("sensor version:", sensor_version, flush=True)           
        process = multiprocessing.Process(target=api.load_scenario_from_directory, args=[self.params, self.result_queue])
        process.start()
        self.after(1, self.check_process_result, process, self.result_queue)

    def select_dir(self):
        select_folder_dir = fd.askdirectory(title='Open data directory',initialdir=self.params.get_parameter('folder_dir'))
        self.params.update_parameter("scenario_folder_dir", select_folder_dir)
        self.step1run_button.configure(state="active")
        self.console_frame.insert_text("Scenario directory selected : " + self.params.get_parameter('scenario_folder_dir') + '\n') 