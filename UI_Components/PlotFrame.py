from tkinter import Label,LabelFrame,Button,Frame,Checkbutton, BooleanVar
from tkinter.ttk import Combobox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from UI_Components.Table3 import Table3

import asyncio
import json
import copy
from pathlib import Path
import os
from os.path import exists
import csv
from API import rapid_api as api

class PlotFrame(LabelFrame):
    def __init__(self, master,console_frame, params, scenario_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
        self.console_frame = console_frame
        self.scenario_data = scenario_data
        self.configure(text = "Visualisation",)
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.fig = plt.Figure()
        self.plot_canvas = FigureCanvasTkAgg(self.fig, self)
        self.plot_canvas.get_tk_widget().grid(row=1, column=0,columnspan=10, sticky='nsew',padx=5, pady=5)
        self.fig.subplots_adjust( bottom=None,  top=None, wspace=None, hspace=None)
        self.frame_tool = Frame(self)
        self.frame_tool.grid(row=4, rowspan=1, column=0,columnspan=7,sticky='ew')
        self.toolbar = NavigationToolbar2Tk(self.plot_canvas, self.frame_tool)

        self.mark_done_button = Button(self,text='Mark as Labeled',command=self.mark_deployment_labeled)
        self.mark_done_button.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nsw',padx=5)
        self.mark_faulty_button = Button(self,text='Mark as Faulty',command=self.mark_deployment_faulty)
        self.mark_faulty_button.grid(row=0, column=1,rowspan=1,columnspan=1, sticky='nsw')

        self.toggle_p_var = BooleanVar()
        self.toggle_a_var = BooleanVar()

        self.toggle_a_var.set(True)
        self.toggle_p_var.set(True)
        
       
        self.toggle_pressure = Checkbutton(self, text="Pressure", variable=self.toggle_p_var, command=self.toggle_pressure )
        self.toggle_pressure.grid(row=0, column=2,rowspan=1,columnspan=1, sticky='nsew')
        self.toggle_accleration= Checkbutton(self, text="Acceleration", variable=self.toggle_a_var, command=self.toggle_accleration)
        self.toggle_accleration.grid(row=0, column=3,rowspan=1,columnspan=1, sticky='nsew')
        

        self.next_button = Button(self,text='Next', command=self.load_next_deployment)
        self.next_button.grid(row=0, column=4,rowspan=1,columnspan=1, sticky='nsew')

        self.prev_button = Button(self,text='Prev', command=self.load_prev_deployment)
        self.prev_button.grid(row=0, column=5,rowspan=1,columnspan=1, sticky='nsew')

        self.reset_button = Button(self,text='Reset',command=self.reset_deployment_fig)
        self.reset_button.grid(row=0, column=6,rowspan=1,columnspan=1, sticky='nsew')

        self.label = Label(self, text = "Deployments :")
        self.label.grid(row=0, column=7,rowspan=1,columnspan=1, sticky='nsew')

        self.fig_combo = Combobox(self, width=30,state = "readonly")
        self.fig_combo.grid(row=0, column=8,rowspan=1,columnspan=1, sticky='nsew')
        self.fig_combo.bind("<<ComboboxSelected>>", self.on_fig_combo_select)

        self.table_3_button = Button(self, text="compute statistics", command= self.compute_statistics)
        self.table_3_button.grid(row=5, column=0, sticky="w")

        # export data button
        self.table_3_export = Button(self, text="export", command= self.export_scenario_data)
        self.table_3_export.grid(row=5, column=1, sticky="w", pady=10)

        #frame for table 3 statisticsL
        self.table_3_frame = Frame(self)
        self.table_3_frame.grid(row=7, column=0,rowspan=1,columnspan=10, sticky='nsew',padx=5, pady=5)
        self.table_3_frame.grid_remove()
        self.table = ""
        self.table3_label = Label(self.table_3_frame, text="This is a label")

    def set_ref_to_compare_frame(self, ref):
        self.ref_to_compare_frame = ref

    def get_ref_to_compare_frame(self, ref):
        return self.ref_to_compare_frame

    def toggle_pressure(self):
        value = not self.params.get_parameter("toggle_pressure")
        self.params.update_parameter("toggle_pressure", value )
        self.reload_deployment_fig()

    def toggle_accleration(self):
        value = not self.params.get_parameter("toggle_accleration")
        self.params.update_parameter("toggle_accleration", value )
        self.reload_deployment_fig()

###################################################################################################################################
    # NEW
    def export_scenario_data(self):
        # get the scenario data 
        sd = self.scenario_data.get_scenario_data_for_computation()

        if(sd['labeled']):
            print("exporting scenario data")
            self.console_frame.insert_text("Exporting scenario data")
            
            
            # choose only labelled runs
            runs_to_use = []
            for r in sd["runs"]:
                #at least 1 run is fully labelled
                if(r["labeled"] == True):
                    runs_to_use.append(r)

            # get the normalised data for the scenario - should be all the deployments in the runs
            if(len(runs_to_use) > 0):

                # this is wrong and duplicates from computing statistics
                result = api.normalise_deployments_for_runs(runs_to_use, self.params)

                """
                norm_data is the key in each deployment object for the data
                norm_data = {
                    'ts_pre':new_ts_pre,
                    'i_to_n_resampled': i_to_n_resampled,
                    'ts_post':new_ts_post,
                    'n_to_t_resampled':n_to_t_resampled,
                    "x_t_norm" : np.concatenate((new_ts_pre,new_ts_post)),
                    "y_p_resampled" : np.concatenate((i_to_n_resampled, n_to_t_resampled)),
                    "a_mag_resampled": a_mag_resampled,
                }
                """
            
                for r in result:
                    print(r.keys(), sd["name"], r["name"], len(r["deployments"]))

                # now we have the normalised data we want to export it to csv files
                # dirs = scenario name, run name, deployment name -> file

                #if export dir does not yet exisit create it
                exports_dir = self.params.get_parameter('export_dir')

                if not exists(exports_dir):
                    os.makedirs(exports_dir)
                    print(f"Directory '{exports_dir}' created successfully in the current working directory!")

                scenario_dir_path = os.path.join(exports_dir, sd["name"])

                if not os.path.exists(scenario_dir_path):
                    os.makedirs(scenario_dir_path)
                    print(f"Created subdirectory: {scenario_dir_path}")
                else:
                    print(f"Subdirectory already exists: {scenario_dir_path}")

                for r in result:
                    # create a dir for the run
                    run_path = os.path.join(scenario_dir_path, r["name"])
                    if not os.path.exists(run_path):
                        os.makedirs(run_path)
                        print(f"Created subdirectory: {run_path}")

                    for d in r["deployments"]:
                        d_path = os.path.join(run_path, d["name"])
                        if not os.path.exists(d_path):
                            os.makedirs(d_path)
                            print(f"Created subdirectory: {d_path}")

                
                # write the data to csv files in the correct directory
                for r in result:
                    run_path = os.path.join(exports_dir, sd["name"], r["name"])
                    for d in r["deployments"]:
                        d_path = os.path.join(run_path, d["name"])
                        filename = f"{d['name']}.csv"
                        filepath = os.path.join(d_path, filename)
                        os.makedirs(d_path, exist_ok=True)
                        data_to_write = list(zip(d["norm_data"]["x_t_norm"], d["norm_data"]["y_p_resampled"], d["norm_data"]["a_mag_resampled"]))
                        with open(filepath, mode='w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(["y_p", "a_mag"])  # Optional header
                            writer.writerows(data_to_write)

                # compute the statistcs
                result = api.compute_passage_and_normalise_for_a_run_sync(runs_to_use, self.params)
                sd["consolidated_scenario_data"] = api.consolidate_runs_for_scenario(sd, self.params)
                sd["table_3_stats"] = api.compute_table_3_statistics(sd)
                stats_dict = sd["table_3_stats"]

                # write to csv in scenario name dir
                csv_path = os.path.join(exports_dir, sd["name"], "stats_summary.csv")
                with open(csv_path, mode='w', newline='') as f:
                    writer = csv.writer(f)

                    # Extract headers from one of the inner dicts
                    headers = ["Measurement"] + list(next(iter(stats_dict.values())).keys())
                    writer.writerow(headers)

                    # Write each row
                    for stat_name, values in stats_dict.items():
                        row = [stat_name] + list(values.values())
                        writer.writerow(row)
                self.console_frame.insert_text("Exported")
                self.console_frame.insert_text("Check exports directory")
            else:
                self.console_frame.insert_text("Cannot export") 
                self.console_frame.insert_text("There are no runs")
        else:
            self.console_frame.insert_text("Cannot export") 
            self.console_frame.insert_text("The scenario is not completely labeled") 

###################################################################################################################################

    def compute_statistics(self):
        print("computing statistics", flush=True)
        sd = self.scenario_data.get_scenario_data_for_computation()

        runs_to_use = []
        for r in sd["runs"]:
            #at least 1 run is fully labelled
            if(r["labeled"] == True):
                runs_to_use.append(r)

        #if("labeled" in sd.keys()):
        if(len(runs_to_use) > 0):
            if(sd['labeled']): # this checks that the scenario is completely labelled
                #result = api.compute_passage_and_normalise_for_a_run_sync(sd["runs"], self.params)
                result = api.compute_passage_and_normalise_for_a_run_sync(runs_to_use, self.params)
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
            selected_deployment = self.fig_combo.get().split(" (")[0]
            self.scenario_data.set_selected_deployment(selected_deployment)
            selected_run = self.scenario_data.get_selected_run()
            scenario_data = self.scenario_data.get_scenario_data()

            for r in scenario_data["runs"]:
                if(r["name"] == selected_run):
                    for index, d in enumerate(r["deployments"]):
                        if (d["name"] == selected_deployment):

                            #should be a function
                            if(d["is_faulty"] == True):
                                self.mark_faulty_button.configure(text="Undo Faulty")
                            else:
                                self.mark_faulty_button.configure(text="Mark as Faulty")

                            deployment_plot = api.create_pressure_plot(self.scenario_data, d, self.fig, self.params)
                            self.scenario_data.set_selected_deployment_index(index)
            
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)

            self.fig.canvas.draw()
            

        else:
            self.console_frame.insert_text("No more deployments" + "\n") 

    def load_next_deployment(self):
        index = self.fig_combo.current()
        num_deployments = len(self.fig_combo['values'])

        if(index < num_deployments-1):
            self.fig_combo.current(index+1)
            selected_deployment = self.fig_combo.get().split(" (")[0]
            self.scenario_data.set_selected_deployment(selected_deployment)
            selected_run = self.scenario_data.get_selected_run()
            scenario_data = self.scenario_data.get_scenario_data()

            for r in scenario_data["runs"]:
                if(r["name"] == selected_run):
                    for index, d in enumerate(r["deployments"]):
                        if (d["name"] == selected_deployment):
                            if(d["is_faulty"] == True):
                                self.mark_faulty_button.configure(text="Undo Faulty")
                            else:
                                self.mark_faulty_button.configure(text="Mark as Faulty")
                            deployment_plot = api.create_pressure_plot(self.scenario_data, d, self.fig, self.params)
                            self.scenario_data.set_selected_deployment_index(index)

            
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)
            self.fig.canvas.draw()
            for ax in self.fig.get_axes():
                ax.autoscale(False)
            

        else:
            self.console_frame.insert_text("No more deployments") 
        
    def mark_deployment_faulty(self):
        #label the deployment as faulty 
        # a faulty deployment will not be used in any further data processing
        run_name = self.scenario_data.get_selected_run()
        deployment_index = self.scenario_data.get_selected_deployment_index()
        scenario = self.scenario_data.get_scenario_data()
        for r in scenario['runs']:
            if(r["name"] == run_name):
                deployment = r["deployments"][deployment_index]
                if(deployment["is_faulty"]):
                    # has been previously marked as faulty so resetting
                    deployment["is_faulty"] = False
                    #reset the scenario labelled parameter 
                    self.mark_faulty_button.configure(text="Mark as Faulty")

                    ##############
                   # lets try to update the combobox
                    selected_deployment = self.fig_combo.get().split(' (')[0]
                    all_items = copy.deepcopy(self.fig_combo['values'])
                    new_item_list = []
                    for idx, item in enumerate(all_items):
                        item_name = item.split(" (")[0]
                        if(item_name == selected_deployment):
                            new_item_list.append(item_name + " " + "(not labelled)")
                            self.fig_combo.set(new_item_list[idx])
                        else:
                            new_item_list.append(item)
                    self.fig_combo['values'] = new_item_list

                    r["labeled"] = False
                    scenario['labeled'] = False

                else:
                    ## MARKING AS FAULTY
                    deployment["is_faulty"] = True

                    if 'pressure_roi' in deployment:
                        del deployment['pressure_roi']

                    self.mark_faulty_button.configure(text="Undo Faulty")

                    # lets try to update the combobox
                    selected_deployment = self.fig_combo.get().split(' (')[0]
                    all_items = copy.deepcopy(self.fig_combo['values'])
                    new_item_list = []
                    for idx, item in enumerate(all_items):
                        item_name = item.split(" (")[0]
                        if(item_name == selected_deployment):
                            new_item_list.append(item_name + " " + "(faulty)")
                            self.fig_combo.set(new_item_list[idx])
                        else:
                            new_item_list.append(item)
                
                    self.fig_combo['values'] =  new_item_list

                    ############
                    all_deploymnets = all('labeled' in obj and obj['labeled'] is True or obj["is_faulty"] is True for obj in r["deployments"])

                    if(all_deploymnets):
                        r["labeled"] = True
                        #at least one run is labeled
                        values_list = self.ref_to_compare_frame.scenario_A_combo['values']
                        if(scenario["name"] not in values_list):
                            self.ref_to_compare_frame.scenario_A_combo['values'] = (*self.ref_to_compare_frame.scenario_A_combo['values'], scenario["name"])
                            self.ref_to_compare_frame.scenario_B_combo['values'] = (*self.ref_to_compare_frame.scenario_B_combo['values'], scenario["name"])
                        else:
                            r["labeled"] = False

                    all_runs = all('labeled' in obj and obj['labeled'] is True for obj in scenario["runs"])

                    if(all_runs):
                        scenario["labeled"] = True
                    else:
                        scenario["labeled"] = False

        # recrete the pressure plot?
        new_plot = api.create_pressure_plot(deployment, self.fig,self.params)
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)

        self.fig.canvas.draw()
        for ax in self.fig.get_axes():
                ax.autoscale(False)

        #revert to original scenario object at loading
        scenario_to_save = {
            "name": scenario["name"],
            "runs": scenario["runs"],
            "labeled": scenario["labeled"]
        }

        #write the data
        write_data = api.write_scenario_to_json_file(scenario_to_save, self.params)

        if(write_data):
            print("scenario written succcesfully")
            self.console_frame.clear_console()
            self.console_frame.insert_text("deployment " + self.scenario_data.get_selected_deployment() + " marked as faulty" + '\n')
            self.console_frame.insert_text("Scenario " + self.scenario_data.get_scenario_data()["name"] + " saved succesfully" '\n') 

    def mark_deployment_labeled(self):
        # check 3 points are on the scenarion_data.pressure_roi object
        is_correctly_marked = False
        is_not_empty = True
        roi_object = self.scenario_data.get_pressure_roi()
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
                    deployment["pressure_roi"] = combined_roi
                    is_correctly_marked=True
                elif("pressure_roi" in  deployment.keys()):
                    # we have the original
                    is_correctly_marked = True
       
                all_deploymnets = all('labeled' in obj and obj['labeled'] is True or obj["is_faulty"] is True for obj in r["deployments"])

                if(all_deploymnets):
                    r["labeled"] = True
                    #at least one run is labeled
                    values_list = self.ref_to_compare_frame.scenario_A_combo['values']
                    if(scenario["name"] not in values_list):
                        self.ref_to_compare_frame.scenario_A_combo['values'] = (*self.ref_to_compare_frame.scenario_A_combo['values'], scenario["name"])
                        self.ref_to_compare_frame.scenario_B_combo['values'] = (*self.ref_to_compare_frame.scenario_B_combo['values'], scenario["name"])
                else:
                    r["labeled"] = False

        if(is_correctly_marked):
            #update combobox
            selected_deployment = self.fig_combo.get().split(' (')[0]
            all_items = copy.deepcopy(self.fig_combo['values'])
            new_item_list = []
            for idx, item in enumerate(all_items):
                item_name = item.split(" (")[0]
                if(item_name == selected_deployment):
                    new_item_list.append(item_name + " " + "(labeled)")
              
                    self.fig_combo.set(new_item_list[idx])
                else:
                    new_item_list.append(item)
            self.fig_combo['values'] =  new_item_list
            # move on

            #remove the saved roi points on scenarion data
            print("removing saved points")
            self.scenario_data.clear_pressure_roi()
            self.load_next_deployment()

            self.fig_combo['values'] = new_item_list
            #if all the runs are done then label the scenario
            all_runs = all('labeled' in obj and obj['labeled'] is True for obj in scenario["runs"])
            if(all_runs):
                scenario["labeled"] = True
            else:
                scenario["labeled"] = False
            
            scenario_to_save = {
                "name": scenario["name"],
                "runs": scenario["runs"],
                "labeled": scenario["labeled"]
            }

            write_data = api.write_scenario_to_json_file(scenario_to_save, self.params)

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
        selected_deployment = self.scenario_data.get_selected_deployment()
        scenario_data = self.scenario_data.get_scenario_data()
        selected_run = self.scenario_data.get_selected_run()
        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for d in r["deployments"]:
                    if (d["name"] == selected_deployment):
                        if(d["is_faulty"] == True):
                            self.mark_faulty_button.configure(text="Undo Faulty")
                        else:
                            self.mark_faulty_button.configure(text="Mark as Faulty")
                        deployment_plot = api.create_pressure_plot(self.scenario_data,d, self.fig, self.params)
        
        
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)

        self.fig.canvas.draw()
        for ax in self.fig.get_axes():
                ax.autoscale(False)
    
    def reset_deployment_fig(self):
        print("resetting deployment")
        selected_deployment = deployment = self.scenario_data.get_selected_deployment()
        scenario_data = self.scenario_data.get_scenario_data()
        selected_run = self.scenario_data.get_selected_run()

        self.scenario_data.clear_pressure_roi()

        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for d in r["deployments"]:
                    if (d["name"] == selected_deployment):
                        if "is_faulty" in d:
                            d["is_faulty"] == False
                            self.mark_faulty_button.configure(text="Mark as Faulty")
                        
                        # remove roi_points from the deployment
                        #deployment_dict["pressure_roi"] = {} # empty set of pressure labels
                        d["pressure_roi"] = {}
                        d["labeled"] = False
                        selected_deployment = self.fig_combo.get().split(' (')[0]
                        all_items = copy.deepcopy(self.fig_combo['values'])
                        new_item_list = []
                        for idx, item in enumerate(all_items):
                            item_name = item.split(" (")[0]
                            if(item_name == selected_deployment):
                                new_item_list.append(item_name + " " + "(not labeled)")
                        
                                self.fig_combo.set(new_item_list[idx])
                            else:
                                new_item_list.append(item)
                        self.fig_combo['values'] =  new_item_list
                        deployment_plot = api.create_pressure_plot(self.scenario_data,d, self.fig, self.params)
        
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)

        self.fig.canvas.draw()
        for ax in self.fig.get_axes():
                ax.autoscale(False)

        scenario_to_save = {
            "name": scenario_data["name"],
            "runs": scenario_data["runs"],
            "labeled": scenario_data["labeled"]
        }

        #save out the data
        write_data = api.write_scenario_to_json_file(scenario_to_save, self.params)

        if(write_data):
            print("scenario written succcesfully")
            self.console_frame.clear_console()
            self.console_frame.insert_text("Scenario " + self.scenario_data.get_scenario_data()["name"] + " saved succesfully" '\n') 
            self.console_frame.insert_text("Pressure ROI values " + json.dumps(self.scenario_data.get_pressure_roi())+ " saved succesfully" '\n') 
            #clear roi points 
            self.scenario_data.clear_pressure_roi()
        print("done")


    def on_pick(self, event): 
        line = event.artist
        if not len(event.ind):  #check the index is valid
            return True
        ind = event.ind[0]
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        ind = event.ind
        
        roi_point = self.scenario_data.get_selected_roi_point()
        print("labelling", roi_point,"with", (int(ind[0]), float(ydata[ind[0]] )))

        #over right any previous point
        self.scenario_data.set_pressure_roi_point(roi_point, (int(ind[0]), float(ydata[ind[0]])))
        prev_roi_points = self.scenario_data.get_pressure_roi()
        
        labels = []
        indexes = []
        values = []
        # locally set prev points
        for key, value in prev_roi_points.items():
            labels.append(key)
            indexes.append(xdata[value[0]]) # doesnt have to be xdata (value[0] should be the same)
            values.append(value[1])
              # we have set a previous point
            if(key == roi_point):
                x_coord = 0
                y_coord = 0
                annotations = self.fig.get_axes()[1].texts
                print("annotations", annotations)
                collections = self.fig.get_axes()[1].collections
                for index, a in enumerate(reversed(annotations)):
                    if(a.get_text() == roi_point):
                        #original_index = len(annotations) - index - 1
                        #self.fig.get_axes()[1].texts.remove(original_index)
                        a.remove()
                        x_coord=a.xy[0]
                        y_coord=a.xy[1]
                        
                
                for index, c in enumerate(reversed(collections)):
                    offsets = c.get_offsets()
                    for o in offsets:
                        if(o[0] == x_coord and o[1]==y_coord):
                            #original_index = len(collections) - index - 1
                            #self.fig.get_axes()[1].collections.remove(original_index)
                            c.remove()
                
            # plot the values
            self.fig.get_axes()[1].scatter(indexes, values)
            for idx,l in enumerate(labels):
                self.fig.get_axes()[1].annotate(l,(indexes[idx],values[idx]) )

        self.fig.canvas.draw()       
    
    def on_fig_combo_select(self, event):
        selected_deployment = self.fig_combo.get().split(' (')[0]
        self.scenario_data.set_selected_deployment(selected_deployment)
        selected_run = self.scenario_data.get_selected_run()

        scenario_data = self.scenario_data.get_scenario_data()

        for r in scenario_data["runs"]:
            if(r["name"] == selected_run):
                for index, d in enumerate(r["deployments"]):
                    print(d["name"], selected_deployment)
                    if (d["name"] == selected_deployment):
                        deployment_plot = api.create_pressure_plot(self.scenario_data, d, self.fig, self.params)
                        self.scenario_data.set_selected_deployment_index(index)
                        if(d["is_faulty"]):
                            self.mark_faulty_button.configure(text="Undo Faulty")

        
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.draw()
        for ax in self.fig.get_axes():
                ax.autoscale(False)