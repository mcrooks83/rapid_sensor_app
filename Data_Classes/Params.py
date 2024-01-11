from numpy import array

class Parameters:

    def __init__(self):
        #main parameters dict (prob not need as they can all be class members)
        self.parameters ={}
        #matrice regroupant les abcisses de chaque limite de section pour tous les tests
        self.parameters['sect']=array([[]])

        #nombre de sections
        self.parameters['nb_sect']=0

        # active/désactive le mode "traçage de section" sur une figure
        self.parameters['click_sect']=False

        # adresse des différents fichiers
        self.parameters['folder_dir']= '' #'/Users/mcrooks/desktop/RightStep/RIGHTSTEP/PROJECTS/TalTech/data'
        self.parameters['save_fold']=''
        self.parameters['sectFile']=''
        self.parameters['output_dir_name'] = 'scenario_outputs'
        self.parameters['complete__scenarios'] = 'complete_scenarios'
        self.parameters['select_folder_dir'] = ""
        self.parameters['roi_points_file'] = "roi_points.json"

        #v2 default
        self.parameters["sensor_version"] = 2
        self.parameters['fs'] = 100 #sample rate in Hz
        self.parameters['fs_p'] = 100 #sample rate of pressure sensor in Hz
        self.parameters['fs_hg'] = 2000
        self.parameters['packet_length'] = 29 #size of bytes per line
        self.parameters['step_size']  = 20

        # paramètres de base du rapid sensor
        self.parameters['fmt'] = '>h' #big-endian binary format

        self.parameters['p_gain'] = 10
        self.parameters['acc_gain'] = 10

        self.parameters["accel_max_window"] = 20

        # mode de filtrage temporel par défaut 
        self.parameters['time_filter']='None'
        self.parameters['time_interval']=[] # intervalle de traitement en secondes
        
        # resampling N
        self.parameters['resample_N']= 10000
        
        #h for total acclimation - user set
        self.parameters['h_min'] = 2.36
        self.parameters['h_max'] = 4
        
        self.working_dir = ""

    
    def add_loaded_scenario(self, value):
        self.loaded_scenarios.append(value)
    def update_parameter(self, key, value):
        self.parameters[key] = value

    def get_parameter(self, key):
        return self.parameters.get(key)
    
    def remove_parameter(self, key):
        if key in self.parameters:
            del self.parameters[key]
    
    def get_all_parameters(self):
        return self.parameters
