from tkinter import IntVar, Toplevel,Label,LabelFrame,Button,Entry,StringVar,Radiobutton
from API import rapid_api as api

class AcclimationDepth(LabelFrame):
    def __init__(self, master,console_frame, params, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.params = params
       
        self.console_frame = console_frame
        self.configure(text = "Set Acclimation Depth",)
        self.grid(row=2, column=0,rowspan=1,columnspan=1, sticky='nesw')
        self.grid_columnconfigure(2, weight=1)


        h_max_default = StringVar(value=params.get_parameter("h_max"))
        h_min_default = StringVar(value=params.get_parameter("h_min"))


        self.min_label = Label(self, text="Max Depth")
        self.min_label.grid(row=1, column=0, columnspan=1)
        self.max_h_entry = Entry(self, textvariable=h_max_default, validate="key", width=10)
        self.max_h_entry.grid(row=1, column=1,columnspan=1,sticky='nws', pady=5 )

        self.min_label = Label(self, text="Min Depth")
        self.min_label.grid(row=2, column=0, columnspan=1)
        self.min_h_entry = Entry(self, textvariable=h_min_default, validate="key", width=10)
        self.min_h_entry.grid(row=2, column=1,columnspan=1,sticky='nws', pady=5  )

        self.set_button = Button(self, text="Set Depths", command=self.validate_numbers, )
        self.set_button.grid(row=3, column=2, sticky="e", padx=5, pady=5)

        self.validation_label = Label(self, text="")
        self.validation_label.grid(row=3, column=0, columnspan=2)

    def clear_label(self):
        self.validation_label.config(
                    text=f"",
                    
                )

    def validate_numbers(self):
        max_data = self.max_h_entry.get()
        min_data = self.max_h_entry.get()

        if max_data and min_data:
            try:
                float(max_data)
                float(min_data)
                self.validation_label.config(
                    text=f"Set Acclimation Depth",
                    foreground="green",
                )
                self.params.update_parameter("h_max", max_data)
                self.params.update_parameter("h_min", min_data)
                self.after(2000, self.clear_label)
            except ValueError:
                self.validation_label.config(
                    text=f'Numeric value expected',
                    foreground="red",
                )
                self.after(2000, self.clear_label)
        else:
            self.validation_label.config(
                text="Entry is empty",
                foreground="red",
            )
            self.after(2000, self.clear_label)

       
    
    