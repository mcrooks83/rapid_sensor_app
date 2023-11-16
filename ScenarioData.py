
class ScenarioData:

    def __init__(self):
        #list of files that exist or have been added
        self.loaded_scenarios = []
        #holds the current working scenario data
        self.scenario_data = {}

        self.selected_run = ""
        self.selected_deployment = ""
        self.selected_deployment_indx = 0

        self.is_marked = False

        # set as first point 
        self.selected_roi_point = "Injection"
        self.pressure_roi = {}
    
    #expects value to be a tuple of (index, value)
    def set_is_marked(self, value):
        self.is_marked = value
    def get_is_marked(self):
        return self.is_marked
    def set_pressure_roi_point(self, key, value):
        self.pressure_roi[key] = value
    def get_pressure_roi(self):
        return self.pressure_roi
    def clear_pressure_roi(self):
        self.pressure_roi = {}

    def add_loaded_scenarios(self, scenarios):
        self.loaded_scenarios = scenarios
    def add_loaded_scenario(self, scenario):
        self.loaded_scenarios.append(scenario)

    def get_loaded_scenarios(self):
        return self.loaded_scenarios

    def add_scenario_data(self, scenario):
        self.scenario_data = scenario
    def get_scenario_data(self):
        return self.scenario_data
    
    def set_selected_run(self, run):
        self.selected_run = run
    def get_selected_run(self):
        return self.selected_run
    
    def set_selected_deployment(self, deployment):
        self.selected_deployment = deployment
    def get_selected_deployment(self):
        return self.selected_deployment
    
    def set_selected_deployment_index(self, index):
        self.selected_deployment_index = index
    def get_selected_deployment_index(self):
        return self.selected_deployment_index

    def set_selected_roi_point(self, roi_point):
        self.selected_roi_point = roi_point
    def get_selected_roi_point(self):
        return self.selected_roi_point