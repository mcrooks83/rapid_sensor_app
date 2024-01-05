from tkinter import IntVar, Toplevel,Label,LabelFrame,Button,Entry,StringVar,Radiobutton
from API import rapid_api as api

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