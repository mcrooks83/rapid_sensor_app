### IMPORTS ###
from mmap import mmap, ACCESS_READ
from struct import unpack
from math import sqrt
from glob import glob 
from os import chdir, mkdir,listdir,remove,getcwd, makedirs
from os.path import splitext, isdir, exists
import numpy as np
import time
import asyncio
import json
import copy
import asyncio
import numpy as np
from scipy.signal import find_peaks
from scipy.signal import resample
import statistics
import matplotlib.pyplot as plt

### HELPERS ###

def make_scenario_list(s1, s2):
    s_list = []
    s_list.append(s1)
    s_list.append(s2)
    return s_list
def get_total_acclimation_pressure(h, local_atmos_pressure):
    rho = 997.05 #density of water
    g = 9.81 #gravitational acceleration
    water_pressure= (rho * g * h)/100
    local_atmos_pressure = 1000
    total_acclimation_pressure = local_atmos_pressure + water_pressure
    return total_acclimation_pressure

#### LOAD SCENARIO ####

# this function will need to be ammended as more sensor outputs come online
# and will differ between v1 and v2
def create_data_axes(data, params):
    #create lists of axis data
    x_t  = []
    y_p = []
    for ind, val in enumerate(data): 
        
        if(params.get_parameter("sensor_version")==1):
            xt = ind / params.get_parameter('fs')
            x_t.append(xt)
            if(len(val) > 2):
                yp = (val[4]-1000)*0.01
                y_p.append(yp)
            else:
                yp = (val[0]-1000)*0.01
                y_p.append(yp)

        else:
            x_t.append(val[0])
            y_p.append(val[4])

        # temps en secondes sur toute la longeur de l'eesai
        #yp = val[4]#(val[4]-1000)*0.01 
        #y_p.append(yp) # pression en mH2O - 10m H2O (la pression est nulle à la surface et est équivalente à la profondeur du sensor. A 2m de profondeur la pression vaut 2 mH2O).
        # add acceleration to this
    return x_t, y_p


# this unpacking is v1 and packet lenght is 11    
def unpacking(row,params): 
    list_values = []
    index = unpack('>h', bytes(row[0:2]))[0]
    index = index - 1
    list_values.append(index)
    
    acc_x = unpack('>h', bytes(row[2:4]))[0]
    acc_x = float(acc_x) / params.get_parameter('acc_gain')
    list_values.append(acc_x)
    acc_y = unpack('>h', bytes(row[4:6]))[0]
    acc_y = acc_y / params.get_parameter('acc_gain')
    list_values.append(acc_y)
    acc_z = unpack('>h', bytes(row[6:8]))[0]
    acc_z = acc_z / params.get_parameter('acc_gain')
    list_values.append(acc_z)
    pressure = unpack('>h', bytes(row[8:10]))[0] 
    pressure = pressure / params.get_parameter('p_gain')
    list_values.append(pressure)
    amag = round(sqrt(pow(acc_x, 2) + pow(acc_y, 2) + pow(acc_z, 2)),2)
    list_values.append(amag)
    return list_values


# this needs clarification for time axis
def unpacking_v2_format(row,params): 
    
    list_values = []

    # 0
    index = unpack('>I', bytes(row[0:4]))[0]
    index = (index / params.get_parameter("fs")) / params.get_parameter("step_size")
    list_values.append(index)
    
    #1
    acc_x = unpack('>h', bytes(row[4:6]))[0]
    acc_x = float(acc_x) / params.get_parameter('acc_gain')
    list_values.append(acc_x)
    #2
    acc_y = unpack('>h', bytes(row[6:8]))[0]
    acc_y = acc_y / params.get_parameter('acc_gain')
    list_values.append(acc_y)
    #3
    acc_z = unpack('>h', bytes(row[8:10]))[0]
    acc_z = acc_z / params.get_parameter('acc_gain')
    list_values.append(acc_z)
    #4,5,6 (gyro) 7,8,9 magnetometer, 10 = pressure 
    pressure = unpack('>H', bytes(row[22:24]))[0]
    pressure = pressure /params.get_parameter('p_gain')
    list_values.append(pressure)
    
    # additioal
    amag = round(sqrt(pow(acc_x, 2) + pow(acc_y, 2) + pow(acc_z, 2)),2)
    list_values.append(amag)
    return list_values

# works for both v2 and v1
def read_row(mm, params):
    count = 0
    while True:
        count += 1
        row = mm.read(params.get_parameter('packet_length')) 
        if not len(row) == params.get_parameter('packet_length'): 
            break 
        yield row

def get_results(filename, params):
    with open(filename,'rb') as file:
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        if(params.get_parameter("sensor_version") == 1):
            results = [unpacking(row,params) for row in read_row(mm,params)]
    return results

def get_v1_pressure_results_only(filename, param):
    results = []
    with open(filename,'rb') as file:
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        row_size = param.get_parameter("packet_length") # should be 11
       
        num_rows = len(mm) // row_size
        print(row_size, num_rows)
        # only read multiples of 20
        #results = [unpacking(row,param) for row in read_row(mm,param)]
        
        # loop over every 20th row (2khz - 100hz ratio)
        for i in range(0, num_rows, 20):
            offset = i * row_size
            mm.seek(offset)  # Move to the starting position of the row
            row = mm.read(row_size)
            results.append(unpacking(row,param))
        
        mm.close()
        file.close() 
    return results

def get_results_v2_format(filename, param):
    with open(filename,'rb') as file:
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        results = [unpacking_v2_format(row,param) for row in read_row(mm,param)]
    return results

def pre_process_file(deployment, data, deployment_number, params):
    print("processing: ", deployment)
    deployment_dict = {}
    name_of_deployment ='Test n°' + str(deployment_number) + ' ' + splitext(deployment)[0]
    deployment_dict["name"] = name_of_deployment
    deployment_dict['sensor_type'] = "FBS" # or BDS
    x_t, y_p = create_data_axes(data, params)
    deployment_dict['x_t']=x_t
    deployment_dict['y_p']=y_p
    
    return deployment_dict

def load_scenario_from_directory(params, result_queue):
    scenario_dir = params.get_parameter('scenario_folder_dir')
    sensor_version = params.get_parameter("sensor_version")
    print(scenario_dir, flush=True)
    #get into the scenario directory
    chdir(r"{}".format(scenario_dir))
 
    scenario_name = scenario_dir.split("/")[-1]
    print("loading scenario", scenario_name)
    scenario_data={}
    scenario_data["name"] = scenario_name
    scenario_data["runs"] = []
    
    # load all runs in the scenario
    # could parallelise this if too slow
    print(listdir("."))
    directory_list = listdir(".")
    for run_dir_name in directory_list:
        print(run_dir_name)
        if isdir(run_dir_name):
            print("loading run", run_dir_name)
            run_data = {
                "name": run_dir_name,
                "deployments" : []
            }
            chdir(r"{}".format(run_dir_name))

            if(sensor_version == 1):
                print("sensor version: 1")
                deployments = glob('*txt')
            else:
                print("sensor version: 2")
                deployments= glob('*.IMP')
                
            print("deployments in run", deployments)
            
            # if there are files to read
            if deployments:
                deployment_number=0
                
                t1=time.time()
                for d in deployments:
                    if(sensor_version == 1):
                        #res = get_results(d, params)
                        res = get_v1_pressure_results_only(d, params)
                    else:
                        res = get_results_v2_format(d, params)
                    deployment_result = pre_process_file(d, res, deployment_number, params)
                    run_data["deployments"].append(deployment_result)
                    deployment_number=deployment_number+1
                t2=time.time()
                print(("It takes %s seconds to load data ") % (t2 - t1))
            
                #add to the scenario
                scenario_data["runs"].append(run_data)
            
            chdir(r"{}".format(scenario_dir))

    chdir(r"{}".format(params.get_parameter('working_dir')))

    for r in scenario_data["runs"]:
        print(r["name"])
    #results = []
    #results.append("done")
    #results.append(scenario_data)
    #result_queue.put(copy.deepcopy(scenario_data), block=True)
    result_queue.put(scenario_data, block=True)
    if(result_queue.empty()):
        print("empty queue")
       
    else:
        print("has data in api")
    
    #result_queue = scenario_data
    return scenario_data

def write_scenario_to_json_file(s, params):
    output_dir = params.get_parameter("output_dir_name")
    working_dir = params.get_parameter("working_dir")
    # Check if the directory exists in the current working directory, and if not, create it
    if not exists(output_dir):
        makedirs(output_dir)
        print(f"Directory '{output_dir}' created successfully in the current working directory!")
    else:
        print(f"Directory '{output_dir}' already exists in the current working directory.")

    filename = s["name"]
    # Writing to sample.json

    with open(working_dir + "/" + output_dir + "/" + filename + ".json", "w") as outfile:
        json.dump(s, outfile)
    
    return True


def read_scenario_from_json_file(params, scenario_name):
    # Opening JSON file
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("output_dir_name") + "/" + scenario_name + ".json", 'r') as openfile:
        print(openfile)
        # Reading from json file
        scenario_data = json.load(openfile)
        return scenario_data
        #print(scenario["name"])
        #print(len(scenario["runs"][0]["deployments"]))
        #print(type(scenario))  

def read_roi_points(params):
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("roi_points_file"), 'r') as openfile:
        roi_points = json.load(openfile)
        return roi_points
    
def write_roi_points(roi_points, params):
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("roi_points_file"), 'w') as openfile:
        json.dump(roi_points, openfile)

def define_box_properties(ax, plot_name, color_code, label):
    #ax.plot([], c=color_code, label=label)
    ax.legend()

def mean_scenario_pressure(s):
    return np.mean(s["consolidated_scenario_data"]['s_normalised_pressure_matrix'], axis=0)


def create_mean_diff_plots(scenarios, fig):
    fig.clear()
    plot_dict = {}
    ax = fig.subplots(2,1)

    count = 0
    mean_pressures = []
   
    # compute mean pressures for each scenario 
    for s in scenarios:
        mean_pressures.append(mean_scenario_pressure(s))
    
    for mp in mean_pressures:
        if((count % 2) == 0):
            ax[0].plot(s["consolidated_scenario_data"]['s_normalised_time_matrix'][0], mp, color="blue", linewidth=2)
        else:
            ax[0].plot(s["consolidated_scenario_data"]['s_normalised_time_matrix'][0], mp, color="orange", linewidth=2)
        count = count + 1
    # currently assumes 2 scenarios are compared
    mean_diff = mean_pressures[0] - mean_pressures[1]
    ax[1].scatter(s["consolidated_scenario_data"]['s_normalised_time_matrix'][0], mean_diff, color="red", s=3)



def create_fig_7_pressure_and_rpc_plots(scenarios, fig):
    fig.clear()
    plot_dict = {}
    ax = fig.subplots(2,2)
    ax[0][0], ax[0][1] = create_fig_7_pressure_plots(scenarios, ax[0][0], ax[0][1])
    ax[1][0], ax[1][1] = create_fig_7_rpc_plots(scenarios, ax[1][0], ax[1][1])

def create_fig_7_rpc_plots(scenarios, ax1, ax2):
    #fig.clear()
     ## BOX PLOTS
    plot_dict = {}
    #ax = fig.subplots(1,2)
    #loop over scenarios for the boxplot
    for idx, s in enumerate(scenarios):
        if(s["name"] in plot_dict):
            s["name"] = s["name"]+ "_" + str(idx)
        plot_dict[s["name"]] = []
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_rpc_min_values'])
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_rpc_max_values'])
    
    ticks =[ "Minimum","Maximum"]
    count = 0
    for key in plot_dict:
        if((count % 2) == 0):
            define_box_properties(ax1, ax1.boxplot(plot_dict[key],
                                                       positions=np.array(np.arange(len(plot_dict[key]))), widths=0.6, boxprops=dict(color='#D7191C')), '#D7191C', key) 
        else:
            define_box_properties(ax1, ax1.boxplot(plot_dict[key],
                                                       positions=np.array(np.arange(len(plot_dict[key]))), widths=0.6, boxprops=dict(color='#2C7BB6')), '#2C7BB6', key)
        count = count + 1
           
        count = count + 1
    ax1.set_xticks(np.arange(0, len(ticks)), ticks)

    run_labels = []
    max_rpcs = []
    min_rpcs = []
    s1_labels = []
    for idx, s in enumerate(scenarios):
        if(idx==0):
           s1_labels.extend(s["consolidated_scenario_data"]["s_run_names"])
        run_labels.extend(s["consolidated_scenario_data"]["s_run_names"])
        max_rpcs.extend(s["consolidated_scenario_data"]["s_rpc_max_values"])
        min_rpcs.extend(s["consolidated_scenario_data"]["s_rpc_min_values"])
    
    indexed_list = list(enumerate(min_rpcs))
    # Sort the indexed list based on the values (second element of each pair)
    sorted_min_rpc_tuple = sorted(indexed_list, key=lambda x: x[1])

    # Extract the original indices from the sorted list
    sorted_min_rpc_indices = [index for index, value in sorted_min_rpc_tuple]
    sorted_min_rpcs = []
    sorted_max_rpcs = []
    sorted_labels = []
    for i in sorted_min_rpc_indices:
        sorted_max_rpcs.append(max_rpcs[i])
        sorted_labels.append(run_labels[i])
        sorted_min_rpcs.append(min_rpcs[i])

    max_colors = ['m' if l in s1_labels else 'b' for l in sorted_labels]
    min_colors = ['c' if l in s1_labels else 'orange' for l in sorted_labels]
    
    bars = ax2.bar(sorted_labels, sorted_max_rpcs, color=max_colors, label="sorted max rpc ")
    ax2.bar(sorted_labels, sorted_min_rpcs, color=min_colors, label="sorted min rpc ")
    #ax[1].tick_params(axis='x', labelrotation=90, labelsize=5, pad=0, top=True, bottom=False)
    ax2.set_xticks([])
    ax2.legend()
    ax2.bar_label(bars, labels=sorted_labels, label_type='center', fontsize=8, color='black', rotation=90)

    return ax1, ax2

def create_fig_7_pressure_plots(scenarios, ax1, ax2):
    #fig.clear()
     ## BOX PLOTS
    plot_dict = {}
    #ax = fig.subplots(1,2)
    
    #loop over scenarios for the boxplot
    for idx, s in enumerate(scenarios):
        if(s["name"] in plot_dict):
            s["name"] = s["name"]+ "_" + str(idx)
        plot_dict[s["name"]] = []
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_min_pressure_values'])
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_max_pressure_values'])
    
    ticks =[ "Minimum","Maximum"]
    count = 0
    for key in plot_dict:
        if((count % 2) == 0):
            define_box_properties(ax1, ax1.boxplot(plot_dict[key],
                                positions=np.array(np.arange(len(plot_dict[key])))*2.0+0.35, widths=0.4, boxprops=dict(color='#D7191C')), '#D7191C', key) 
        else:
            define_box_properties(ax1, ax1.boxplot(plot_dict[key],
                                positions=np.array(np.arange(len(plot_dict[key])))*2.0-0.35, widths=0.4, boxprops=dict(color='#2C7BB6')), '#2C7BB6', key)
        count = count + 1
    ax1.set_xticks(np.arange(0, len(ticks) * 2, 2), ticks)

    run_labels = []
    max_pressures = []
    min_pressures = []
    s1_labels = []
    for idx, s in enumerate(scenarios):
        if(idx==0):
           s1_labels.extend(s["consolidated_scenario_data"]["s_run_names"])

        run_labels.extend(s["consolidated_scenario_data"]["s_run_names"])
        max_pressures.extend(s["consolidated_scenario_data"]["s_max_pressure_values"])
        min_pressures.extend(s["consolidated_scenario_data"]["s_min_pressure_values"])
    
    indexed_list = list(enumerate(min_pressures))
    # Sort the indexed list based on the values (second element of each pair)
    sorted_min_pressure_tuple = sorted(indexed_list, key=lambda x: x[1])

    # Extract the original indices from the sorted list
    sorted_min_pressure_indices = [index for index, value in sorted_min_pressure_tuple]
    sorted_min_pressures = []
    sorted_max_pressures = []
    sorted_labels = []
    
    for i in sorted_min_pressure_indices:
        sorted_max_pressures.append(max_pressures[i])
        sorted_labels.append(run_labels[i])
        sorted_min_pressures.append(min_pressures[i])

    max_colors = ['m' if l in s1_labels else 'b' for l in sorted_labels]
    min_colors = ['c' if l in s1_labels else 'orange' for l in sorted_labels]

    bars = ax2.bar(sorted_labels, sorted_max_pressures, color=max_colors, label="sorted max pressures")
    ax2.bar(sorted_labels, sorted_min_pressures, color=min_colors, label="sorted min pressures")
    #ax[1].tick_params(axis='x', labelrotation=90, labelsize=5, pad=0, top=True, bottom=False)
    ax2.set_xticks([])
    ax2.legend()
    ax2.bar_label(bars, labels=sorted_labels, label_type='center', fontsize=8, color='black', rotation=90)

    return ax1, ax2


def create_fig_6_box_plots(scenarios, fig):
    fig.clear()  
    plot_dict = {}
    ax = fig.subplots()
    
    for idx, s in enumerate(scenarios):
        #if comparing the same named scenario
        if(s["name"] in plot_dict):
            s["name"] = s["name"]+ "_" + str(idx)

        plot_dict[s["name"]] = []
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_injection_to_nadir_duration_values'])
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_nadir_to_tailwater_duration_values'])
        plot_dict[s["name"]].append(s["consolidated_scenario_data"]['s_passage_duration_values'])
    
    ticks = ['Injection to Nadir', 'Nadir to Tailwater', 'Total Passage']
    count = 0
    for key in plot_dict:
        if((count % 2) == 0):
            define_box_properties(ax, ax.boxplot(plot_dict[key],positions=np.array(np.arange(len(plot_dict[key])))*2.0-0.35, widths=0.4, boxprops=dict(color='#D7191C')), '#D7191C', key) 
        else:
            define_box_properties(ax, ax.boxplot(plot_dict[key],positions=np.array(np.arange(len(plot_dict[key])))*2.0+0.35, widths=0.4, boxprops=dict(color='#2C7BB6')), '#2C7BB6', key)
        count = count + 1
        
    ax.set_xticks(np.arange(0, len(ticks) * 2, 2), ticks)


def get_scenarios_to_compare(scenario_list, params):
    scenarios = []
    if(len(scenario_list) > 1):
        for s in scenario_list:
            scenario = read_scenario_from_json_file(params, s)
            result = asyncio.run(compute_passage_and_normalise_for_a_run(scenario['runs'], params))
            scenario["consolidated_scenario_data"] = consolidate_runs_for_scenario(scenario, params)
            scenarios.append(scenario)
    return scenarios


def create_pressure_plot(deployment, fig):
    fig.clear()
    ax = fig.subplots()
    ax.set_title(deployment["name"])
    ax.plot(deployment['x_t'], deployment['y_p'], color="blue", linewidth=2, picker=True, pickradius=1)

    if "pressure_roi" in deployment:
        labels = []
        indexes = []
        values = []
        for key, value in deployment["pressure_roi"].items():
            labels.append(key)
            indexes.append(deployment['x_t'][value[0]])
            values.append(value[1])
            ax.scatter(indexes, values)
            for idx,l in enumerate(labels):
                ax.annotate(l,(indexes[idx],values[idx]) )
    
    ax.set_xlabel('Time ')
    ax.set_ylabel('Pressure')
    #ax.legend(('X component','Y component','Z component'))
    ax.grid(True)
    
    #return ax



### 

def detect_key_pressure_points(x_t, y_p, fs):    
    nadir_idx = y_p.index(min(y_p))
    peaks, _ = find_peaks(y_p, prominence=100)
    print("peaks", peaks)
    injection_idx = peaks[0]
    
    #1010 mbar ? 
    tailwater_idx = peaks[-1]+(fs*200)
    if(nadir_idx > injection_idx):
        print("good")
    else:
        print("no good")
        print("I: ",injection_idx, "N: ", nadir_idx)
        nadir_idx = nadir_idx + (fs*500)
        print("I: ",injection_idx, "N: ", nadir_idx)
    
    pressure_roi = {
        "injection": (injection_idx, y_p[injection_idx]),
        "nadir": (nadir_idx, y_p[nadir_idx]),
        "tailwater": (tailwater_idx, y_p[tailwater_idx]),
    }
    print(pressure_roi)
    
    return pressure_roi

def pressure_roi_for_runs(deployments, params):
    for d in deployments:
        pressure_roi = detect_key_pressure_points(d['x_t'], d['y_p'], params.get_parameter('fs') )
        d['pressure_roi'] = pressure_roi


## Compute passage and normalise the data 
def compute_passage_durations(deployment_roi, sampling_frequency):
    injection_to_nadir_duration = deployment_roi["Nadir"][0] - deployment_roi["Injection"][0] / sampling_frequency
    nadir_to_tailwater_duration = deployment_roi["Tailwater"][0] - deployment_roi["Nadir"][0] / sampling_frequency
    passage_duration = deployment_roi["Tailwater"][0] - deployment_roi["Injection"][0] / sampling_frequency
    return {
        "injection_to_nadir_duration":injection_to_nadir_duration,
        "nadir_to_tailwater_duration":nadir_to_tailwater_duration,
        "passage_duration":passage_duration
        
    }

def normalise_deployment_data(deployment, N):
    print(deployment["name"])

    idx_start = deployment['pressure_roi']['Injection'][0]
    idx_stop = deployment['pressure_roi']['Nadir'][0]
    size_pre = idx_stop  - (idx_start + 1)
    ts_pre = np.arange(0, size_pre+1) / (2 * size_pre)
    i_to_n = deployment['y_p'][idx_start:idx_stop+1]
    
    idx_start_post = idx_stop +1
    idx_stop_post = deployment['pressure_roi']['Tailwater'][0]
    #print("index stop post", idx_stop_post)
    size_post = idx_stop_post - (idx_start_post+1);
    #print("size post", size_post)
    ts_post = np.arange(0, size_post+1)/(2*size_post)+0.5;
    #print("ts_post", ts_post)
    n_to_t = deployment['y_p'][idx_start_post:idx_stop_post+1]
    
    #print("pre and post")
    new_ts_pre = np.linspace(ts_pre[0], ts_pre[-1], int(N/2))
    new_ts_post = np.linspace(ts_post[0], ts_post[-1], int(N/2))
    
    i_to_n_resampled = resample(i_to_n, int(N/2))
    i_to_n_resampled[-1]=i_to_n[-1]
    i_to_n_resampled[0]=i_to_n[0]

    n_to_t_resampled = resample(n_to_t,int(N/2))
    n_to_t_resampled[-1]=n_to_t[-1]
    n_to_t_resampled[0] = n_to_t[0]
    
    normalised_data = {
        'ts_pre':new_ts_pre,
        'i_to_n_resampled': i_to_n_resampled,
        'ts_post':new_ts_post,
        'n_to_t_resampled':n_to_t_resampled,
        "x_t_norm" : np.concatenate((new_ts_pre,new_ts_post)),
        "y_p_resampled" : np.concatenate((i_to_n_resampled, n_to_t_resampled))
    }
    
    return normalised_data

async def compute_passage_and_normalise_for_a_deployment(deployment, params):
    print("computing only passasge durations")
    print(deployment["pressure_roi"],  flush=True)
    deployment["passage_durations"] = compute_passage_durations(deployment['pressure_roi'], params.get_parameter('fs'))
    deployment['normalised_data'] = normalise_deployment_data(deployment, params.get_parameter('resample_N'))
    
# assumes all deployments in the run are complete
# this is aysnc but for a demo does not need to be
async def compute_passage_and_normalise_for_a_run(runs, params):
    deployment_list = []
    for r in runs:
        print("computing passage durations and normalising")
        for d in r['deployments']:
            deployment_list.append(compute_passage_and_normalise_for_a_deployment(d, params))
        await asyncio.gather(*deployment_list)   
    return "run"


def consolidate_deployments(deployments, params, h_min, h_max):
    run_names = []
    nadir_values = []
    prc_values = []
    rpc_min_values = []
    rpc_max_values = []
    injection_to_nadir_duration_values = []
    nadir_to_tailwater_duration_values = []
    passage_duration_values = []
    max_pressure_values = []
    min_pressure_values = []
    normalised_time_matrix = []
    normalised_pressure_matrix = []
    
    for d in deployments:
        run_names.append(d["name"])
        nadir_values.append(d['pressure_roi']['Nadir'][1])
        prior_nadir_max_pressure_interval = d['y_p'][ d['pressure_roi']['Nadir'][0]- params.get_parameter('fs') : d['pressure_roi']['Nadir'][0]]  
        prc_values.append(max(prior_nadir_max_pressure_interval) - d['pressure_roi']['Nadir'][1])
        rpc_min_values.append(np.log(get_total_acclimation_pressure(h_min, 1000) / d['pressure_roi']['Nadir'][1]))
        rpc_max_values.append(np.log(get_total_acclimation_pressure(h_max, 1000) / d['pressure_roi']['Nadir'][1]))
        
        injection_to_nadir_duration_values.append(d['passage_durations']['injection_to_nadir_duration'])
        nadir_to_tailwater_duration_values.append(d['passage_durations']['nadir_to_tailwater_duration'])
        passage_duration_values.append(d['passage_durations']['passage_duration'])
        
        #  stats_data['min_max_pressure']["Minimum"].append(min(fig_data["y_p"]))
        max_pressure_values.append(max(d['y_p']))
        min_pressure_values.append(min(d['y_p']))
        
        normalised_time_matrix.append(d['normalised_data']['x_t_norm'])
        normalised_pressure_matrix.append(d['normalised_data']['y_p_resampled'])
    
    consolidated_run_data = {
        "run_names":run_names,
        "nadir_values":nadir_values,
        "prc_values": prc_values,
        "rpc_min_values":rpc_min_values,
        "rpc_max_values":rpc_max_values,
        "injection_to_nadir_duration_values":injection_to_nadir_duration_values,
        "nadir_to_tailwater_duration_values":nadir_to_tailwater_duration_values,
        "passage_duration_values":passage_duration_values,
        "max_pressure_values":max_pressure_values,
        "min_pressure_values":min_pressure_values,
        "normalised_time_matrix":normalised_time_matrix,
        "normalised_pressure_matrix":normalised_pressure_matrix,
    }
    
    return consolidated_run_data

def consolidate_runs_for_scenario(scenario, params):
    s_run_names = []
    s_nadir_values = []
    s_prc_values = []
    s_rpc_min_values = []
    s_rpc_max_values = []
    s_injection_to_nadir_duration_values = []
    s_nadir_to_tailwater_duration_values = []
    s_passage_duration_values = []
    s_max_pressure_values = []
    s_min_pressure_values = []
    s_normalised_time_matrix = []
    s_normalised_pressure_matrix = []
    
    for r in scenario['runs']:
        consolidated_run_data = consolidate_deployments(r['deployments'], params, params.get_parameter("h_min"), params.get_parameter("h_max"))
        r["consolidated_run_data"] = consolidated_run_data
        
        s_run_names.extend([*consolidated_run_data['run_names']])
        s_nadir_values.extend([*consolidated_run_data['nadir_values']])
        s_prc_values.extend([*consolidated_run_data['prc_values']])
        s_rpc_min_values.extend([*consolidated_run_data['rpc_min_values']])
        s_rpc_max_values.extend([*consolidated_run_data['rpc_max_values']])
        s_injection_to_nadir_duration_values.extend([*consolidated_run_data['injection_to_nadir_duration_values']])
        s_nadir_to_tailwater_duration_values.extend([*consolidated_run_data['nadir_to_tailwater_duration_values']])
        s_passage_duration_values.extend([*consolidated_run_data['passage_duration_values']])
        s_max_pressure_values.extend([*consolidated_run_data['max_pressure_values']])
        s_min_pressure_values.extend([*consolidated_run_data['min_pressure_values']])
        
        for n_t in consolidated_run_data['normalised_time_matrix']:
            s_normalised_time_matrix.append(n_t)
        for y_p in consolidated_run_data['normalised_pressure_matrix']:
            s_normalised_pressure_matrix.append(y_p)
    
    consolidated_scenario_data = {
            "s_run_names" : s_run_names,
            "s_nadir_values": s_nadir_values,
            "s_prc_values":s_prc_values,
            "s_rpc_min_values":s_rpc_min_values,
            "s_rpc_max_values":s_rpc_max_values,
       
            "s_injection_to_nadir_duration_values":s_injection_to_nadir_duration_values,
            "s_nadir_to_tailwater_duration_values":s_nadir_to_tailwater_duration_values,
            "s_passage_duration_values":s_passage_duration_values,

            "s_max_pressure_values":s_max_pressure_values,
            "s_min_pressure_values":s_min_pressure_values,
            "s_normalised_time_matrix":s_normalised_time_matrix,
            "s_normalised_pressure_matrix":s_normalised_pressure_matrix, 
    }
    return consolidated_scenario_data


def compute_stats(data):

    mean = statistics.mean(data)
    median = statistics.median(data)
    _max = max(data)
    _min = min(data)
    _range = _max - _min
    q3, q1 = np.percentile(data, [75 ,25])
    IQR = q3 - q1
    std = statistics.stdev(data)
    
    absolute_diff = np.abs(np.array(data) - median)
    mad = np.median(absolute_diff)
    
    return {
        "mean":mean,
        "median":median,
        "max": _max,
        "min": _min,
        "range": _range,
        "q3": q3,
        "q1" : q1,
        "IQR" : IQR,
        "std" : std,
        "mad": mad   
    
    }

def compute_table_3_statistics(scenario):
    table_3_stats = {}
    for key in scenario["consolidated_scenario_data"]:
        if(key != "s_normalised_time_matrix" and key != "s_normalised_pressure_matrix" and key !="s_run_names"):
            table_3_stats[key] = compute_stats(scenario["consolidated_scenario_data"][key])
    return table_3_stats