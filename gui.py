
## imports
from os.path import splitext,join,isdir,dirname
from pandas import read_excel, read_csv
from glob import glob 
from os import chdir, mkdir,listdir,remove, getcwd
import asyncio
import json
import concurrent.futures
import threading 
import queue
import multiprocessing
from queue import Queue

#tkinter
from tkinter import E,W,S,N, IntVar, Toplevel,BOTH, INSERT,END,Tk,PanedWindow,Label,LabelFrame,CENTER,Button,Frame,Entry,RIGHT,StringVar,Radiobutton,Checkbutton,Text,Scrollbar, Listbox
from tkinter import filedialog as fd
from tkinter.ttk import Combobox, Progressbar, Treeview

#from numpy import min,shape,sort,isnan,zeros,ones,array
#from matplotlib.pyplot import close,ioff,Figure
#from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

from matplotlib.pyplot import close,ioff,Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

import Params as p
from UI_Components.Console import ConsoleFrame as console
import ScenarioData as sd
from UI_Components.Title import Title

from Functions.read_me import read_me_text, readme_heading_text
from API import rapid_api as api



#### Main UI using Tkinter ###

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
        #self.step_one = StepOneFrame(self)
    
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
        print("read me called")
        self.console_frame.configure_state("normal")
        self.console_frame.insert_text(readme_heading_text)
        self.console_frame.tag_config('manual_mess', foreground='green', underline=1)
        self.console_frame.insert_text(read_me_text)
        self.console_frame.configure_state(state ='disabled')
   


class LeftFrame(Frame):
    def __init__(self, master, console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params=params
        self.scenario_data = scenario_data
        self.plot_frame = plot_frame
        self.console_frame = console_frame
        
        #self.config(bg=bg_color)
        #self.pack(fill='both', expand=True)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.sidebar = SideBar(self,self.console_frame, self.params, self.scenario_data, self.plot_frame)
        #console buttons
        self.button_frame = ButtonFrame(self, self.console_frame, self.params, self.scenario_data)

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

class ProcessFrame(Frame):
    def __init__(self, master, console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params=params
        self.scenario_data = scenario_data
        self.plot_frame = plot_frame
        #self.configure(bg=bg_color)
        self.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.load_scenario_data_frame = LoadScenarioData(self, console_frame, self.params, self.scenario_data, self.plot_frame)
        self.label_roi_frame = LabelROIFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame)
        self.compare_scenarios_frame = CompareScenariosFrame(self, console_frame, self.params, self.scenario_data, self.plot_frame)

class CompareScenariosFrame(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data = scenario_data
        self.console_frame = console_frame
        self.plot_frame = plot_frame
        self.configure(text = "Compare Scenarios",)
        self.grid(row=2, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(2, weight=1)

        self.loaded_scenarios_A = Label(self, text = "1st Scenario : ")
        self.loaded_scenarios_A.grid(row=2, column=0, columnspan=1, sticky='e')
        self.scenario_A_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_A_combo.grid(row=2, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)

        self.loaded_scenarios_B = Label(self, text = "2nd Scenario : ")
        self.loaded_scenarios_B.grid(row=3, column=0, columnspan=1, sticky='e')
        self.scenario_B_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_B_combo.grid(row=3, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)

        for item in self.scenario_data.get_loaded_scenarios():
            self.scenario_A_combo['values'] = (*self.scenario_A_combo['values'], item)
            self.scenario_B_combo['values'] = (*self.scenario_B_combo['values'], item)
        
        self.scenario_A_combo.bind("<<ComboboxSelected>>", self.on_first_scenario_select)
        self.scenario_B_combo.bind("<<ComboboxSelected>>", self.on_second_scenario_select)

        # future
        self.scenarios_to_compare = []
        self.first_scenario_name = ""
        self.second_scenario_name = ""

        self.compare_button_frame = Frame(self)
        self.compare_button_frame.grid(row=5, column=0, columnspan=2)
        self.compare_scenarios = Button(self.compare_button_frame,text='Box Plots', command=self.compare_scenarios_with_box_plots)
        self.compare_scenarios.grid(row=5, column=0,sticky='ws',pady=5 )
        self.compare_scenarios = Button(self.compare_button_frame,text='Pressure / PRC Plots', command=self.compare_scenarios_pressure_and_rpc)
        self.compare_scenarios.grid(row=5, column=1,sticky='ws',pady=5 )
        self.compare_scenarios = Button(self.compare_button_frame,text='Mean / Diff', command=self.compare_scenarios_mean_diff)
        self.compare_scenarios.grid(row=5, column=2,sticky='ws',pady=5 )


    def compare_scenarios_mean_diff(self):
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

    def compare_scenarios_rpc(self):
        self.plot_frame.table_3_frame.grid_remove()
        scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
        scenarios = api.get_scenarios_to_compare(scenarios, self.params)
        plot = api.create_fig_7_rpc_plots(scenarios, self.plot_frame.fig)
        self.plot_frame.fig.canvas.draw()

    def compare_scenarios_pressure(self):
        self.plot_frame.table_3_frame.grid_remove()
        scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
        scenarios = api.get_scenarios_to_compare(scenarios, self.params)
        plot = api.create_fig_7_pressure_plots(scenarios, self.plot_frame.fig)
        self.plot_frame.fig.canvas.draw()

    def compare_scenarios_with_box_plots(self):
        self.plot_frame.table_3_frame.grid_remove()
        scenarios = api.make_scenario_list(self.first_scenario_name, self.second_scenario_name)
        scenarios = api.get_scenarios_to_compare(scenarios, self.params)
        plot = api.create_fig_6_box_plots(scenarios, self.plot_frame.fig)
        self.plot_frame.fig.canvas.draw()

    def on_first_scenario_select(self, event):
        first_selected_scenario = self.scenario_A_combo.get()
        print(first_selected_scenario)
        self.first_scenario_name  = first_selected_scenario
        self.scenarios_to_compare.append(first_selected_scenario)
    
    def on_second_scenario_select(self, event):
        #note disable this out until first is selected
        second_selected_scenario = self.scenario_B_combo.get()
        print(second_selected_scenario)
        self.second_scenario_name  = second_selected_scenario
        self.scenarios_to_compare.append(second_selected_scenario)

class LabelROIFrame(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data = scenario_data
        self.console_frame = console_frame
        self.configure(text = "Label ROI",)
        self.grid(row=1, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(2, weight=1)

        # read from roi_points.json and create a radio button for each
        # could load this file on selection of a deployment or loading of a run in previous step
        self.roi_var = IntVar()

        roi_points = api.read_roi_points(self.params)
        for p in roi_points:
            #this isnt quite right but seems to work
            button_name = p["name"].lower() + "_" + "roi_button"
            self.button_name = Radiobutton(self, text=p["name"], value=p["id"], variable = self.roi_var, command=self.select_roi_point)
            self.button_name.grid(row=0,column=p["id"],columnspan=1,sticky='w',pady=5)
            
        self.add_roi_button = Button(self,text='New ROI', command=self.add_new_roi)
        self.add_roi_button.grid(row=2, column=0,columnspan=1,sticky='ws',pady=5 )
    
    def add_new_roi(self):
        print("add new roi")
        add_roi_window = Toplevel(self.master)
        add_roi_window.title("Add ROI")
    
        # sets the geometry of toplevel
        add_roi_window.geometry("300x100")
 
        roi_input = StringVar()
        roi_label = Label(add_roi_window, text = "ROI name: ")
        roi_label.grid(row=0, column=0, columnspan=1, sticky='e',pady=5, padx=5)         
        roi_entry= Entry(add_roi_window, textvariable=roi_input)
        roi_entry.grid(row=0, column=1, columnspan=1,sticky='w',pady=5, padx=5)

        save_roi_button = Button(add_roi_window, text="Add ROI", command= lambda: self.save_new_roi(roi_input.get(), roi_added_label))
        save_roi_button.grid(row=1, column=0, columnspan=2,sticky='w',padx=5,pady=5)
        roi_added_label = Label(add_roi_window, text="")
        roi_added_label.grid(row=2, column=0,  sticky='w', padx=5)
        


    def save_new_roi(self, roi_text, roi_added_label):         
        if roi_text:
            roi_points = api.read_roi_points(self.params)
            new_id = len(roi_points)
            roi_point_to_add = {
                "id": new_id,
                "name": roi_text,
                "comment": ""
            }
            roi_points.append(roi_point_to_add)
            api.write_roi_points(roi_points, self.params)

            button_name = roi_text.lower() + "_" + "roi_button"
            self.button_name = Radiobutton(self, text=roi_text, value=new_id, variable = self.roi_var, command=self.select_roi_point)
            self.button_name.grid(row=0,column=new_id,columnspan=1,sticky='w',pady=5)

            roi_added_label.config(text="added " + roi_text + " roi")
        else:
            roi_added_label.config(text="no roi added")

        

    def select_roi_point(self):
        roi_selected = self.roi_var.get()
        if(roi_selected == 0):
            print("Injection")
            self.scenario_data.set_selected_roi_point("Injection")
        elif(roi_selected == 1):
            print("Nadir")
            self.scenario_data.set_selected_roi_point("Nadir")
        elif(roi_selected == 2):
            print("Tailwater")
            self.scenario_data.set_selected_roi_point("Tailwater")


class LoadScenarioData(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, plot_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.scenario_data =scenario_data
        self.plot_frame = plot_frame
        self.console_frame = console_frame
       
        self.configure(text = "Load Scenario",)
        self.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(1, weight=1)

        self.data_dir = Label(self, text = "Sensor Version : ")
        self.data_dir.grid(row=0, column=0, )

        #set inital radio button to either v1 or v2
        self.sensor_version_var = IntVar()
        self.sensor_version_var.set(params.get_parameter("sensor_version"))
        self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " 2048 Hz" '\n') 
        #self.sensor_version_var = params.get_parameter("sensor_version")
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
        self.step1run_button = Button(self.step1button_frame,text='Load Scenario ',command=self.load_scenario)
        self.step1run_button.grid(row=0, column=1, columnspan=1, sticky='ew',padx=5,pady=5)
   
        #list box of all loaded scenarios
        self.loaded_scenarios = Label(self, text = "Scenarios : ")
        self.loaded_scenarios.grid(row=2, column=0, columnspan=1, sticky='e')

        self.scenario_combo = Combobox(self,  width=20,state = "readonly")
        self.scenario_combo.grid(row=2, column=1,rowspan=1,columnspan=1, sticky='nw',padx=5)

        self.selected_scenario = Label(self, text="")
        self.selected_scenario.grid(row=2, column=3,columnspan=1, sticky='nw',padx=5)

        #self.listbox = Listbox(self)
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
        #self.pbar_ind.grid_remove()
        self.blank = Frame(self.progress_bar_frame)
        self.blank.grid(row=7, column=0, columnspan=7, sticky="news")
        self.result_queue = multiprocessing.Queue()


    def update_sensor_version(self):
        if(self.sensor_version_var.get() == 1):
            self.console_frame.clear_console()
            #self.console_frame.display_title_text()
            self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " 2048 Hz" '\n') 
            self.params.update_parameter("sensor_version", self.sensor_version_var.get())
            self.params.update_parameter("fs", 2048)
            self.params.update_parameter("packet_length", 11)
        elif(self.sensor_version_var.get() == 2):
            self.console_frame.clear_console()
            #self.console_frame.display_title_text()
            self.console_frame.insert_text("Sensor version:  v" + str(self.sensor_version_var.get()) + " 100 Hz" '\n') 
            self.params.update_parameter("sensor_version", self.sensor_version_var.get())
            self.params.update_parameter("fs", 100)
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
                    self.plot_frame.fig_combo['values'] = (*self.plot_frame.fig_combo['values'], d['name'])

    def on_scenario_combo_select(self, event):
         # get sensor version from the radio buttons

        selected_scenario = self.scenario_combo.get()
        print("Loading scenario", flush=True)
        
        self.selected_scenario.config(text={selected_scenario})

        s_data = api.read_scenario_from_json_file(self.params, selected_scenario)
        self.scenario_data.add_scenario_data(s_data)

        #update run list
        for r in s_data["runs"]:
            #my_combobox.configure(values=())
            self.run_combo.configure(values=())
            self.run_combo.set("")
            self.run_combo['values'] = (*self.run_combo['values'], r['name'])
        #fself.console_frame.clear_console()
        self.console_frame.insert_text("Loaded " + s_data["name"] + "" '\n') 

    def start_loading_progress(self):
        self.pbar_ind.start()

    def stop_loading_progress(self):
        print("stop progress")
        self.pbar_ind.stop()
        self.pbar_ind.config(mode="indeterminate")

    
    def load_scenario(self):
        print("loading scenario")
        self.console_frame.insert_text("Loading scenario ..." + '\n') 
        self.pbar_ind.tkraise()
        self.start_loading_progress()
        sensor_version = self.sensor_version_var.get()
        print("sensor version:", sensor_version, flush=True)

        def check_process_result(process, result_queue):
            try:
                scenario_data = result_queue.get(block=False)
                print("loading completed")
                self.stop_loading_progress()
                #self.pbar_ind.grid_remove()
                self.pbar_ind.lower()

                if scenario_data:
                #write data to json file for later
                    print("writing data")
                    write_data = api.write_scenario_to_json_file(scenario_data, self.params)
                    if(write_data):
                        self.scenario_data.add_loaded_scenario(scenario_data["name"])
                        print("scenario written succcesfully")
                        #self.console_frame.clear_console()
                        self.console_frame.insert_text("Scenario " + scenario_data["name"] + " saved succesfully" '\n') 
                    #add to combox
                    if scenario_data["name"] not in self.scenario_combo['values']:
                        self.scenario_combo['values'] += (scenario_data["name"],)
                
            except queue.Empty:
                # Handle the case where the queue is empty
                self.after(1, check_process_result, process, self.result_queue)

                
        process = multiprocessing.Process(target=api.load_scenario_from_directory, args=[self.params, self.result_queue])
        process.start()
           
        self.master.after(1, check_process_result, process, self.result_queue)


    def select_dir(self):
        select_folder_dir = fd.askdirectory(title='Open data directory',initialdir=self.params.get_parameter('folder_dir'))
        self.params.update_parameter("scenario_folder_dir", select_folder_dir)
        self.console_frame.insert_text("Scenario directory selected : " + self.params.get_parameter('scenario_folder_dir') + '\n') 


class Table3(Treeview):
    def __init__(self, parent):
        super().__init__(parent, column=("Measurement", "Mean", "Median", "Max", "Min", "Range", "Q#", "Q1", "IQR", "STD", "MAD"), show='headings',)
        self.parent = parent
        #Measurement", "Mean", "Median", "Max", "Min", "Range", "Q3", "Q1", "IQR", "STD", "MAD"
        # Define column headings
        self.heading("#1", text="Measurement")
        self.heading("#2", text="Mean")
        self.heading("#3", text="Median")
        self.heading("#4", text="Max")
        self.heading("#5", text="Min")
        self.heading("#6", text="Range")
        self.heading("#7", text="Q3")
        self.heading("#8", text="Q1")
        self.heading("#9", text="IQR")
        self.heading("#10", text="STD")
        self.heading("#11", text="MAD")


        # Pack the Treeview widget
        self.pack(fill=BOTH, expand=True)
        self.center_treeview_columns()

        # Bind an event to update column widths when the window is resized
        self.parent.bind("<Configure>", self.update_column_widths)

    def center_treeview_columns(self):
    # Get the column IDs
        columns = self["columns"]
        # Center-align the text in each column
        for col in columns:
            self.column(col, anchor="center")

    def clear_table(self):
        item_count = self.get_children()
        # Delete all items from the treeview
        for item in item_count:
            self.delete(item)
    def insert_data(self, data):
        for item in data:
            self.insert("", "end", values=item)

    def update_column_widths(self, event):
        # Calculate column widths based on the frame width
        frame_width = self.parent.winfo_width()
        column_width = frame_width // 11  # Divide equally among 9 columns

        # Set the column widths
        for col in ("#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11"):
            self.column(col, width=column_width)



class PlotFrame(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.console_frame = console_frame
        self.scenario_data = scenario_data
        self.configure(text = "Visualisation",)
        self.grid_columnconfigure(1, weight=1)
        
        #self.grid_rowconfigure(1, weight=1)
        self.label = Label(self, text = "Deployments :")
        self.label.grid(row=0, column=5,rowspan=1,columnspan=1, sticky='ne')

        self.fig_combo = Combobox(self, width=50,state = "readonly")
        self.fig_combo.grid(row=0, column=6,rowspan=1,columnspan=1, sticky='nw',padx=5)
        self.fig_combo.bind("<<ComboboxSelected>>", self.on_fig_combo_select)

        self.rowconfigure(1, weight=1)
        self.fig = plt.Figure()
        self.plot_canvas = FigureCanvasTkAgg(self.fig, self)
        self.plot_canvas.get_tk_widget().grid(row=1,  column=0,columnspan=7, sticky='nsew',padx=5, pady=5)
        self.fig.subplots_adjust( bottom=None,  top=None, wspace=None, hspace=None)
        self.frame_tool = Frame(self)
        self.frame_tool.grid(row=4, rowspan=1, column=0,columnspan=7,sticky='ew')
        self.toolbar = NavigationToolbar2Tk(self.plot_canvas, self.frame_tool)
       

        self.next_button = Button(self,text='Next', command=self.load_next_deployment)
        self.next_button.grid(row=0, column=2,rowspan=1,columnspan=1, sticky='nw')

        self.prev_button = Button(self,text='Prev', command=self.load_prev_deployment)
        self.prev_button.grid(row=0, column=3,rowspan=1,columnspan=1, sticky='nw')

        self.reset_button = Button(self,text='Reset',command=self.reload_deployment_fig)
        self.reset_button.grid(row=0, column=4,rowspan=1,columnspan=1, sticky='ne',padx=5)

        self.mark_done_button = Button(self,text='Mark as Labeled',command=self.mark_deployment_labeled)
        self.mark_done_button.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='ne',padx=5)
        #self.reset_button.configure(state ='disable')

        self.table_3_button = Button(self, text="compute statistics", command=self.compute_statistics)
        self.table_3_button.grid(row=5, column=0, sticky="w")
        #frame for table 3 statisticsL
        self.table_3_frame = Frame(self)
        self.table_3_frame.grid(row=7, column=0,rowspan=1,columnspan=7, sticky='nsew',padx=5, pady=5)
        self.table_3_frame.grid_remove()
        self.table = ""
        self.table3_label = Label(self.table_3_frame, text="This is a label")

    def compute_statistics(self):
        print("computing statistics", flush=True)
        sd = self.scenario_data.get_scenario_data()
        if("labeled" in sd.keys()):
            if(sd['labeled']):
                result = asyncio.run(api.compute_passage_and_normalise_for_a_run(sd['runs'], self.params))
                print(result)
                sd["consolidated_scenario_data"] = api.consolidate_runs_for_scenario(sd, self.params)
                sd["table_3_stats"] = api.compute_table_3_statistics(sd)

                nadir_values =          sd["table_3_stats"]["s_nadir_values"]
                prc_values =            sd["table_3_stats"]["s_prc_values"]
                s_rpc_min_values =      sd["table_3_stats"]["s_rpc_min_values"]
                s_rpc_max_values =      sd["table_3_stats"]["s_rpc_max_values"]
                s_min_pressure_values = sd["table_3_stats"]["s_min_pressure_values"]
                s_max_pressure_values = sd["table_3_stats"]["s_max_pressure_values"]

                #Measurement", "Mean", "Median", "Max", "Min", "Range", "Q3", "Q1", "IQR", "STD", "MAD"
                data = [
                ("Nadir", round(nadir_values["mean"],2), round(nadir_values["median"],2),round(nadir_values["max"],2),round(nadir_values["min"],2),round(nadir_values["range"],2),round(nadir_values["q3"],2),round(nadir_values["q1"],2), round(nadir_values["IQR"],2), round(nadir_values["std"],2), round(nadir_values["mad"],2)),
                ("PRC", round(prc_values["mean"],2), round(prc_values["median"],2), round(prc_values["max"],2), round(prc_values["min"],2), round(prc_values["range"],2), round(prc_values["q3"],2), round(prc_values["q1"],2), round(prc_values["IQR"],2), round(prc_values["std"],2), round(prc_values["mad"],2)),
                ("RPC MAX", round(s_rpc_max_values["mean"],2), round(s_rpc_max_values["median"],2), round(s_rpc_max_values["max"],2), round(s_rpc_max_values["min"],2), round(s_rpc_max_values["range"],2), round(s_rpc_max_values["q3"],2), round(s_rpc_max_values["q1"],2), round(s_rpc_max_values["IQR"],2), round(s_rpc_max_values["std"],2), round(s_rpc_max_values["mad"],2)),
                ("RPC MIN", round(s_rpc_min_values["mean"],2), round(s_rpc_min_values["median"],2), round(s_rpc_min_values["max"],2), round(s_rpc_min_values["min"],2), round(s_rpc_min_values["range"],2), round(s_rpc_min_values["q3"],2), round(s_rpc_min_values["q1"],2), round(s_rpc_min_values["IQR"],2), round(s_rpc_min_values["std"],2), round(s_rpc_min_values["mad"],2)),
                ("Max Pressure", round(s_max_pressure_values["mean"],2), round(s_max_pressure_values["median"],2), round(s_max_pressure_values["max"],2), round(s_max_pressure_values["min"],2), round(s_max_pressure_values["range"],2), round(s_max_pressure_values["q3"],2), round(s_max_pressure_values["q1"],2), round(s_max_pressure_values["IQR"],2),  round(s_max_pressure_values["std"],2), round(s_max_pressure_values["mad"],2)),      
                ("Min Pressure", round(s_min_pressure_values["mean"],2), round(s_min_pressure_values["median"],2), round(s_min_pressure_values["max"],2), round(s_min_pressure_values["min"],2),round(s_min_pressure_values["range"],2), round(s_min_pressure_values["q3"],2), round(s_min_pressure_values["q1"],2), round(s_min_pressure_values["IQR"],2), round(s_min_pressure_values["std"],2), round(s_min_pressure_values["mad"],2)),
                ]

                if isinstance(self.table, Table3):
                    self.table.clear_table()
                    self.table.insert_data(data)
                    self.table_3_frame.grid()
                else:
                    self.table = Table3(self.table_3_frame)
                    self.table.insert_data(data)
                    self.table_3_frame.grid()
                
            else:
                self.table_3_frame.grid_remove()
                self.console_frame.clear_console()
                self.console_frame.insert_text("The scenario is not completely labeled") 
        else:
            self.table_3_frame.grid_remove()
            self.console_frame.clear_console()
            self.console_frame.insert_text("The scenario is not completely labeled") 

    def load_prev_deployment(self):
        index = self.fig_combo.current()

        prev_index = index - 1
        #num_deployments = len(self.fig_combo['values'])
        print(index, prev_index)
        if(prev_index >= 0):

            self.fig_combo.current(prev_index)
            selected_deployment = self.fig_combo.get()
            self.scenario_data.set_selected_deployment(selected_deployment)
            selected_run = self.scenario_data.get_selected_run()
            scenario_data = self.scenario_data.get_scenario_data()

            for r in scenario_data["runs"]:
                if(r["name"] == selected_run):
                    for index, d in enumerate(r["deployments"]):
                        if (d["name"] == selected_deployment):
                            deployment_plot = api.create_pressure_plot(d, self.fig)
                            self.scenario_data.set_selected_deployment_index(index)

            self.fig.canvas.draw()
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)
        else:
            self.console_frame.insert_text("No more deployments" + "\n") 


    def load_next_deployment(self):
        index = self.fig_combo.current()
        num_deployments = len(self.fig_combo['values'])
        print(index, num_deployments, flush=True)

        if(index < num_deployments-1):

            self.fig_combo.current(index+1)
            selected_deployment = self.fig_combo.get()
            self.scenario_data.set_selected_deployment(selected_deployment)
            selected_run = self.scenario_data.get_selected_run()
            scenario_data = self.scenario_data.get_scenario_data()

            for r in scenario_data["runs"]:
                if(r["name"] == selected_run):
                    for index, d in enumerate(r["deployments"]):
                        if (d["name"] == selected_deployment):
                            deployment_plot = api.create_pressure_plot(d, self.fig)
                            self.scenario_data.set_selected_deployment_index(index)

            self.fig.canvas.draw()
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)
        else:
            self.console_frame.insert_text("No more deployments") 
        
    def mark_deployment_labeled(self):
        # check 3 points are on the scenarion_data.pressure_roi object
        is_correctly_marked = False
        is_not_empty = True
        roi_object = self.scenario_data.get_pressure_roi()
        print(roi_object, flush=True)
        if not roi_object:
            is_not_empty = False
        
        keys_len = len(roi_object.keys())

        run_name = self.scenario_data.get_selected_run()
        deployment_index = self.scenario_data.get_selected_deployment_index()

        # find the deployment
        scenario = self.scenario_data.get_scenario_data()

        for r in scenario['runs']:
            if(r["name"] == run_name):
                deployment = r["deployments"][deployment_index]
                #if we have a complete roi_object then use this
                if(is_not_empty and keys_len > 2):
                    deployment["pressure_roi"] = roi_object
                    deployment["labeled"] = True
                    is_correctly_marked=True
                elif(is_not_empty):
                    #we have some rois and need to combine with what is stored
                    combined_roi = {k: roi_object[k] if k in roi_object else v for k, v in deployment["pressure_roi"].items()}
                    print(combined_roi, flush=True)
                    deployment["pressure_roi"] = combined_roi
                    is_correctly_marked=True
                elif("pressure_roi" in  deployment.keys()):
                    # we have the original
                    print("we have the origanl rois", flush=True)
                    is_correctly_marked = True
       
                all_deploymnets = all('labeled' in obj and obj['labeled'] is True for obj in r["deployments"])

                if(all_deploymnets):
                    r["labeled"] = True
                else:
                    r["labeled"] = False

        if(is_correctly_marked):
            self.load_next_deployment()
            #if all the runs are done then label the scenario
            all_runs = all('labeled' in obj and obj['labeled'] is True for obj in scenario["runs"])
            if(all_runs):
                scenario["labeled"] = True
            else:
                scenario["labeled"] = False
            write_data = api.write_scenario_to_json_file(scenario, self.params)

            if(write_data):
                print("scenario written succcesfully")
                self.console_frame.clear_console()
                self.console_frame.insert_text("Scenario " + self.scenario_data.get_scenario_data()["name"] + " saved succesfully" '\n') 
                self.console_frame.insert_text("Pressure ROI values " + json.dumps(self.scenario_data.get_pressure_roi())+ " saved succesfully" '\n') 
                #clear roi points 
                self.scenario_data.clear_pressure_roi()
            print("done")
        else:
            self.console_frame.clear_console()
            self.console_frame.insert_text("Deployment has not been correctly labeled") 

    def reload_deployment_fig(self):
        selected_deployment = deployment = self.scenario_data.get_selected_deployment()
        scenario_data = self.scenario_data.get_scenario_data()
        selected_run = self.scenario_data.get_selected_run()
        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for d in r["deployments"]:
                    if (d["name"] == selected_deployment):
                        deployment_plot = api.create_pressure_plot(d, self.fig)
        
        self.fig.canvas.draw()
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)

    
    def on_pick(self, event):
        #self.fig.get_axes()[0].scatter.remove()
        line = event.artist
        if not len(event.ind):  #check the index is valid
            return True
        ind = event.ind[0]
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        ind = event.ind
        
        roi_point = self.scenario_data.get_selected_roi_point()
        #over right any previous point
        self.scenario_data.set_pressure_roi_point(roi_point, (int(ind[0]), float(ydata[ind[0]])))
        prev_roi_point = self.scenario_data.get_pressure_roi()
        print(prev_roi_point)
        print(self.fig.get_axes())
        print(event.artist)

        self.reload_deployment_fig()
        
        labels = []
        indexes = []
        values = []
        for key, value in prev_roi_point.items():
            print(key)
            labels.append(key)
            indexes.append(xdata[value[0]])
            values.append(value[1])
            self.fig.get_axes()[0].scatter(indexes, values)
            for idx,l in enumerate(labels):
                self.fig.get_axes()[0].annotate(l,(indexes[idx],values[idx]) )

        self.fig.canvas.draw()         
        
    
    def on_fig_combo_select(self, event):
        selected_deployment = self.fig_combo.get()
        self.scenario_data.set_selected_deployment(selected_deployment)
        selected_run = self.scenario_data.get_selected_run()
        print(selected_deployment)

        scenario_data = self.scenario_data.get_scenario_data()

        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for index, d in enumerate(r["deployments"]):
                    if (d["name"] == selected_deployment):
                        deployment_plot = api.create_pressure_plot(d, self.fig)
                        self.scenario_data.set_selected_deployment_index(index)
        self.fig.canvas.draw()
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)
        

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

