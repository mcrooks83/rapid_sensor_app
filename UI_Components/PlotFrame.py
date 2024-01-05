from tkinter import Label,LabelFrame,Button,Frame
from tkinter.ttk import Combobox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

from UI_Components.Table3 import Table3

import asyncio
import json
import copy

from API import rapid_api as api

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
        self.label.grid(row=0, column=6,rowspan=1,columnspan=1, sticky='ne')

        self.fig_combo = Combobox(self, width=50,state = "readonly")
        self.fig_combo.grid(row=0, column=7,rowspan=1,columnspan=1, sticky='nw',padx=5)
        self.fig_combo.bind("<<ComboboxSelected>>", self.on_fig_combo_select)

        self.rowconfigure(1, weight=1)
        self.fig = plt.Figure()
        self.plot_canvas = FigureCanvasTkAgg(self.fig, self)
        self.plot_canvas.get_tk_widget().grid(row=1,  column=0,columnspan=8, sticky='nsew',padx=5, pady=5)
        self.fig.subplots_adjust( bottom=None,  top=None, wspace=None, hspace=None)
        self.frame_tool = Frame(self)
        self.frame_tool.grid(row=4, rowspan=1, column=0,columnspan=7,sticky='ew')
        self.toolbar = NavigationToolbar2Tk(self.plot_canvas, self.frame_tool)
       
        self.next_button = Button(self,text='Next', command=self.load_next_deployment)
        self.next_button.grid(row=0, column=3,rowspan=1,columnspan=1, sticky='nw')

        self.prev_button = Button(self,text='Prev', command=self.load_prev_deployment)
        self.prev_button.grid(row=0, column=4,rowspan=1,columnspan=1, sticky='nw')

        self.reset_button = Button(self,text='Reset',command=self.reload_deployment_fig)
        self.reset_button.grid(row=0, column=5,rowspan=1,columnspan=1, sticky='nw',padx=5)

        self.mark_done_button = Button(self,text='Mark as Labeled',command=self.mark_deployment_labeled)
        self.mark_done_button.grid(row=0, column=0,rowspan=1,columnspan=1, sticky='nw',padx=5)

        self.mark_faulty_button = Button(self,text='Mark as Faulty',command=self.mark_deployment_faulty)
        self.mark_faulty_button.grid(row=0, column=1,rowspan=1,columnspan=1, sticky='nw')

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
        sd = self.scenario_data.get_scenario_data_for_computation()
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

                            deployment_plot = api.create_pressure_plot(d, self.fig)
                            self.scenario_data.set_selected_deployment_index(index)

            self.fig.canvas.draw()
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)
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
                            deployment_plot = api.create_pressure_plot(d, self.fig)
                            self.scenario_data.set_selected_deployment_index(index)

            self.fig.canvas.draw()
            self.plot_canvas.mpl_connect('pick_event', self.on_pick)
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
                    else:
                        r["labeled"] = False

                    all_runs = all('labeled' in obj and obj['labeled'] is True for obj in scenario["runs"])

                    if(all_runs):
                        scenario["labeled"] = True
                    else:
                        scenario["labeled"] = False

        # recrete the pressure plot?
        new_plot = api.create_pressure_plot(deployment, self.fig)
        self.fig.canvas.draw()
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)

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
            # move on
            self.load_next_deployment()
    
            #(*self.plot_frame.fig_combo['values'], dep)
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
        selected_deployment = deployment = self.scenario_data.get_selected_deployment()
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

        self.reload_deployment_fig()
        
        labels = []
        indexes = []
        values = []
        for key, value in prev_roi_point.items():
   
            labels.append(key)
            indexes.append(xdata[value[0]])
            values.append(value[1])
            self.fig.get_axes()[0].scatter(indexes, values)
            for idx,l in enumerate(labels):
                self.fig.get_axes()[0].annotate(l,(indexes[idx],values[idx]) )

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
                        deployment_plot = api.create_pressure_plot(d, self.fig)
                        self.scenario_data.set_selected_deployment_index(index)
                        if(d["is_faulty"]):
                            self.mark_faulty_button.configure(text="Undo Faulty")

        self.fig.canvas.draw()
        self.plot_canvas.mpl_connect('pick_event', self.on_pick)