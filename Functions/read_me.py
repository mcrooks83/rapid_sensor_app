readme_heading_text = """\n -| RapidSensorAnalysis User Manual |-\n\n\n"""
read_me_text= """
The RapidSensorAnalysis program extracts acceleration and pressure over the time from the raw data collected by a Rapid sensor. \n
Then, it determines the number of shocks and shears exceeding a user-defined intensity threshold.  \n
Impacts are display in several graphical forms such as histograms, scatter plots or cumulative frequency curves. \n
Time delimitations and subdivisions can be applied to segment the acquisition to retain only the desired events. \n
Results can be saved in csv format and as graphs. \n
The program is divided into 3 steps. When a step is validated, it remains in memory until its next execution. \n
This allows the user to perform a step several times in a row without repeating the previous one. \n\n\n

I. Step 1: Loading data \n \n

Enter the following parameters then press \RUN\ button. \n
Stop the process at any time by pressing the \"STOP\" button. \n\n

- Data directory: load the folder containing sensor data. The file browser only shows folders. \n

- Impact threshold: enter the minimum acceleration threshold to consider the event as a shock/shear. \n\n

The data is loaded and the acceleration threshold is applied. At this moment, only the pressure and acceleration graphs are generated. \n\n\n

II. Step 2: Time filtering \n\n

Choose one of the four methods available, fill the parameters related and press \"RUN\" button. \n
Stop the process at any time by pressing the \"STOP\" button. \n\n

- Time filter = None: no time filter is applied.  \n
Generates shock and shear graphs for all tests. \n\n

- Time filter = Interval: only takes into account events that occurred during the selected time interval. \n
The same interval is applied to all files and corrected if it exceeds the duration of certain tests. \n
Generates shock and shear graphs for the events in the interval only. \n\n

- Time filter = Sections: applies a unique time division for each file. Load an excel file containing the time values. \n
Each line corresponds to a file. It is possible to enter more than two values per line in order to create several sections \n 
Each line must have the same number of values. \n
Generates shock and shear graphs for the events and specify the section in which they are located. \n\n

- Time filter = Click section: draw sections directly on the graphics. \n
Select the number of sections you want. \n
After pressing the \"RUN\" button navigate through the figures. \n
Create a section limit by pressing \"Ctrl + left click\". \n
Reset the current figure by pressing \"Reset fig.\" in the visualization section. \n
When all the sections are drawn, press \"Confirm all\" to process and generates shock and shear graphs. \n\n\n

III. Step 3: Result saving \n\n

Saves all the graphs in .png and the data in .csv. Also exports sections if \"Time filter = Click section\" was chosen. \n 

- Study name: enter the name of your study. \n
- Only ROI for test figures: displays only the time interval studied on the acceleration/pressure graphs. \n\n\n

IV. Console \n \n

The console displays all important information. \n 
It returns parameter entry errors, the progress of the process and the directory of the results file. \n
Press the \"Clear Console\" button to clear the console. \n\n\n

V. Visualization \n\n

All the figures are displayed in the visualization area. \n"
\"Prev.\" and \"Next\" buttons or left and right arrows of the keyboard allows the user to move on to previous or next figure.\n
The drop-down list on the top right allows the user to select a specific figure. \n"
\"Reset fig.\" and \"Confirm all\" are only available for the draw section mode (cf. II. -Time filter = Click section). \n
The figure toolbox is on the bottom left of the visualization area and have all the tools like zoom-in, zoom-out, move etc. \n\n\n
"""