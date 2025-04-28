### IMPORTS ###
from mmap import mmap, ACCESS_READ
from struct import unpack
from math import sqrt
from glob import glob 
from os import chdir, listdir, makedirs
from os.path import splitext, isdir, exists
import numpy as np
import time
import asyncio
import json
import asyncio
import numpy as np
from scipy.signal import resample
import statistics

### HELPERS ###
def make_scenario_list(s1, s2):
    s_list = []
    if s1 != " " and len(s1)>0:
        s_list.append(s1)
    if s2 != " " and len(s2)>0:
        s_list.append(s2)
    return s_list

def get_total_acclimation_pressure(h, local_atmos_pressure):
    rho = 997.05 #density of water
    g = 9.81 #gravitational acceleration
    #print("h is:", h,  type(h))
    water_pressure= (rho * g * h)/100
    local_atmos_pressure = 1000
    total_acclimation_pressure = local_atmos_pressure + water_pressure
    return total_acclimation_pressure


# data will be a list of lists first list will be 100hz and 2nd list will be hig
def create_data_axes(data, params):
    #create lists of axis data
    x_t  = []
    y_p = []
    a_mag = []
    x_t_hig = []
    a_mag_hig = []
    for ind, val in enumerate(data[0]):
        if(params.get_parameter("sensor_version") == 1):
            xt = ind  * 20 / params.get_parameter('fs') 
            x_t.append(xt)
            a_mag.append(val[-1])
        else:
            xt = ind  / params.get_parameter('fs')
            x_t.append(xt)
            a_mag.append(val[5]) # adds the accel_magnitdue
            
        y_p.append(val[4])
    
    if(len(data)>1): # there is hig data
        for ind, val in enumerate(data[1]):
            xt = ind  / params.get_parameter('fs_hg')
            x_t_hig.append(xt)
            a_mag_hig.append(val[-1])

    return x_t, y_p, a_mag, x_t_hig, a_mag_hig

# this unpacking is v1 and packet lenght is 11    
def unpacking(row,params): 
    list_values = []
    index = unpack('>h', bytes(row[0:2]))[0]
    list_values.append(index)
    acc_x = unpack('>h', bytes(row[2:4]))[0]
    acc_x = float(acc_x) / params.get_parameter('acc_gain')
    list_values.append(acc_x)
    acc_y = unpack('>h', bytes(row[4:6]))[0]
    acc_y = float(acc_y) / params.get_parameter('acc_gain')
    list_values.append(acc_y)
    acc_z = unpack('>h', bytes(row[6:8]))[0]
    acc_z = float(acc_z) / params.get_parameter('acc_gain')
    list_values.append(acc_z)
    pressure = unpack('>h', bytes(row[8:10]))[0] 
    pressure = pressure / params.get_parameter('p_gain')
    list_values.append(pressure)
 
    amag = round(sqrt(pow(acc_x, 2) + pow(acc_y, 2) + pow(acc_z, 2)),2)
    list_values.append(amag)
    #np_mag = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

    return list_values

def unpacking_v2_format_hig(row, params):
    list_values = []
    index = unpack('>I', bytes(row[0:4]))[0]
    acc_x = unpack('>h', bytes(row[4:6]))[0]
    acc_y = unpack('>h', bytes(row[6:8]))[0]
    acc_z = unpack('>h', bytes(row[8:10]))[0]

    index = (index / params.get_parameter("fs_hg"))
    list_values.append(index)
    acc_x = float(acc_x) / params.get_parameter('hig_gain')
    list_values.append(acc_x)
    acc_y = acc_y / params.get_parameter('hig_gain')
    list_values.append(acc_y)
    acc_z = acc_z / params.get_parameter('hig_gain')
    list_values.append(acc_z)
    # this is the hig mag
    amag = round(sqrt(pow(acc_x, 2) + pow(acc_y, 2) + pow(acc_z, 2)),2)
    list_values.append(amag)
    return list_values

# this needs clarification for time axis
def unpacking_v2_format(row,params): 
    list_values = []
    # 0
    index = unpack('>I', bytes(row[0:4]))[0]
    acc_x = unpack('>h', bytes(row[4:6]))[0]
    acc_y = unpack('>h', bytes(row[6:8]))[0]
    acc_z = unpack('>h', bytes(row[8:10]))[0]
   
    index = (index / params.get_parameter("fs")) / params.get_parameter("step_size")
    list_values.append(index)
    acc_x = float(acc_x) * params.get_parameter('acc_gain')
    list_values.append(acc_x)
    acc_y = acc_y * params.get_parameter('acc_gain')
    list_values.append(acc_y)
    acc_z = acc_z * params.get_parameter('acc_gain')
    list_values.append(acc_z)

    #4,5,6 (gyro) 7,8,9 magnetometer, 10 = pressure 
    pressure = unpack('>H', bytes(row[22:24]))[0]
    pressure = pressure /params.get_parameter('p_gain')
    list_values.append(pressure)
    
    # additioal in position 5
    amag = round(sqrt(pow(acc_x, 2) + pow(acc_y, 2) + pow(acc_z, 2)),2)
    list_values.append(amag)
    return list_values

def read_row(mm, params, hig=0):
    count = 0
    while True:
        count += 1
        if(hig==0):
            row = mm.read(params.get_parameter('packet_length')) 
            if not len(row) == params.get_parameter('packet_length'): 
                break 
        
        if(hig==1):
            row = mm.read(params.get_parameter('packet_length_hig')) 
            if not len(row) == params.get_parameter('packet_length_hig'): 
                break 
        
        
        yield row

def get_results(filename, params):
    with open(filename,'rb') as file:
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        if(params.get_parameter("sensor_version") == 1):
            results = [unpacking(row,params) for row in read_row(mm,params)]
        mm.close()
        file.close() 
    return results


def get_v1_pressure_results_only(filename, param):
    complete_results = []
    results = []            # holds every 20th row
    with open(filename,'rb') as file:
        print("reading v1 data")
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        accel_max_window = param.get_parameter("accel_max_window")
        prior_rows_to_read = int(accel_max_window / 2)
        row_size = param.get_parameter("packet_length") # should be 11
        num_rows = len(mm) // row_size
        # loop over every 20th row (2khz - 100hz ratio)
        for i in range(0, num_rows, accel_max_window):
            offset = i * row_size                   # offset for each 20th row
            if(i < 100):
                print(offset)
            tmp_max_accel_mag = 0
            start_offset = max(0, offset - (prior_rows_to_read*row_size))
            mm.seek(offset)
            row = mm.read(row_size)                 # read single row 
            unpacked_row = unpacking(row,param)     # unpack single row
            if(start_offset == 0):
                tmp_max_accel_mag = unpacked_row[-1]
            else:
                mm.seek(start_offset)
                # reads 20 * 11 bytes for 20 rows - add 1 to the 
                data_block = mm.read(accel_max_window+1*row_size)    
                # process blocks of 11 bytes
                for i in range(accel_max_window):
                    
                    row_data = data_block[i * 11: (i + 1) * 11]
                    #print(row_data)
                    if(len(row_data) == row_size):
                        unpack_for_accel = unpacking(row_data,param)
                        if(unpack_for_accel[-1]>tmp_max_accel_mag):
                            tmp_max_accel_mag = unpack_for_accel[-1]
            unpacked_row.append(tmp_max_accel_mag)  
            results.append( unpacked_row)
        
        mm.close()
        file.close() 
    complete_results.append(results)
    return complete_results

#######

def get_results_v2_format(filename, hig_filename, param):

    complete_results = []
    # get 100hz presssure / accel
    with open(filename,'rb') as file:
        mm = mmap(file.fileno(), 0, access=ACCESS_READ)
        results = [unpacking_v2_format(row,param) for row in read_row(mm,param)]
        complete_results.append(results)
        mm.close()
        file.close() 
    
    # get the hig
    if hig_filename:
        print("getting results for", hig_filename)
        with open(hig_filename,'rb') as file:
            mm = mmap(file.fileno(), 0, access=ACCESS_READ)
            results = [unpacking_v2_format_hig(row,param) for row in read_row(mm,param, 1)]
            complete_results.append(results)
            mm.close()
            file.close() 
        
    print("completed results", len(complete_results), flush=True)
    return complete_results

def pre_process_file(deployment, data, deployment_number, params):
    deployment_dict = {}
    name_of_deployment ='Test n°' + str(deployment_number) + ' ' + splitext(deployment)[0]
    deployment_dict["name"] = name_of_deployment
    deployment_dict['sensor_type'] = "FBS" # or BDS
    deployment_dict['is_faulty'] = False
    deployment_dict["labeled"] = False
    deployment_dict["pressure_roi"] = {} # empty set of pressure labels
    x_t, y_p, a_mag, x_t_hig, a_mag_hig = create_data_axes(data, params)
    deployment_dict['x_t']=x_t
    deployment_dict['y_p']=y_p
    #deployment_dict['a_mag'] = a_mag

    if(len(a_mag)>0):
        deployment_dict["a_mag"] = a_mag
    
    if(len(a_mag_hig)>0):
        print("writing hig data")
        deployment_dict["x_t_hig"] = x_t_hig
        deployment_dict["a_mag_hig"] = a_mag_hig
    
    return deployment_dict

def load_scenario_from_directory(params, result_queue):
    scenario_dir = params.get_parameter('scenario_folder_dir')
    sensor_version = params.get_parameter("sensor_version")
    print(scenario_dir, flush=True)
    chdir(r"{}".format(scenario_dir))
    scenario_name = scenario_dir.split("/")[-1]
    print("loading scenario", scenario_name)
    scenario_data={}
    scenario_data["name"] = scenario_name
    scenario_data["runs"] = []
    print(listdir("."))
    directory_list = listdir(".")
    
    directory_list = [file for file in directory_list if not file.startswith('.')]

    for idx, run_dir_name in enumerate( directory_list):
        print(f"run {idx+1} of {len(directory_list)} runs")
        result_queue.put({"run_status":{"run_name": run_dir_name, "runs": len(directory_list), "run_no":idx+1}})
       
        if isdir(run_dir_name):
            print("loading run", run_dir_name)
            run_data = {
                "name": run_dir_name,
                "deployments" : [],
                "labeled": False
            }
            chdir(r"{}".format(run_dir_name))

            if(sensor_version == 1):
                print("sensor version: 1")
                deployments = glob('*txt')
            else:
                print("sensor version: 2")
                deployments= glob('*.IMP')
                hig_deployments = glob('*.HIG') # Hi G accleration
                # sort so that 01 is first

            # if there are files to read
            if deployments:
                deployment_number=0
               
                t1=time.time()
                for idx, d in enumerate(deployments):

                    print(f"processing deployment {idx+1} of {len(deployments)} deployments")
                    result_queue.put({"deployment_status": { "deployment_name": d, "deployment_no": deployment_number+1, "deployments": len(deployments)}})

                    if(sensor_version == 1):
                        res = get_v1_pressure_results_only(d, params)
                    else:
                        
                        # list of lists where index 0 is 100hz and 1 is hig accel
                        #what happens if there are no .HIG files?
                        res = get_results_v2_format(d, hig_deployments[idx], params)
                        

                    deployment_result = pre_process_file(d, res, deployment_number, params)
                    run_data["deployments"].append(deployment_result)

                    # data gets put here d is just a file name for updating console with
                    result_queue.put({"d":d})
                    deployment_number=deployment_number+1
                t2=time.time()
                print(("It takes %s seconds to load data ") % (t2 - t1))
                scenario_data["runs"].append(run_data)
            
            chdir(r"{}".format(scenario_dir))

    chdir(r"{}".format(params.get_parameter('working_dir')))

    result_queue.put(scenario_data, block=True)
  
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
    with open(working_dir + "/" + output_dir + "/" + filename + ".json", "w") as outfile:
        json.dump(s, outfile)

    return True

def read_scenario_from_json_file(params, scenario_name):
    # Opening JSON file
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("output_dir_name") + "/" + scenario_name + ".json", 'r') as openfile:
        # Reading from json file
        scenario_data = json.load(openfile)
        return scenario_data

def read_roi_points(params):
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("roi_points_file"), 'r') as openfile:
        roi_points = json.load(openfile)
        return roi_points
    
def write_roi_points(roi_points, params):
    with open(params.get_parameter("working_dir") + "/" + params.get_parameter("roi_points_file"), 'w') as openfile:
        json.dump(roi_points, openfile)

def mean_scenario_pressure(s):
    return np.mean(s["consolidated_scenario_data"]['s_normalised_pressure_matrix'], axis=0)

def create_mean_diff_plots(scenarios, fig):
    fig.clear()
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

def define_box_properties(ax, plot_name, color_code, label):
    #ax.plot([], c=color_code, label=label)
    ax.legend()

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

    if(len(scenarios)>1):
        count = 0
        boxes = []
        labels = []
        for key in plot_dict:
            if((count % 2) == 0):
                bp = ax.boxplot( plot_dict[key],   positions=np.array(np.arange(len(plot_dict[key])))*2.0-0.35,  widths=0.4,  boxprops=dict(color='#D7191C'))
                boxes.append(bp)
                labels.append(key)
            else:
                bp = ax.boxplot(plot_dict[key],   positions=np.array(np.arange(len(plot_dict[key])))*2.0+0.35, widths=0.4, boxprops=dict(color='#2C7BB6'))
                boxes.append(bp)
                labels.append(key)
            count = count + 1
            
        ax.set_xticks(np.arange(0, len(ticks) * 2, 2), ticks)
        ax.set_ylabel('Passage Duration (s)')
        ax.legend([box["boxes"][0] for box in boxes], labels, loc='upper right')

    else:
        #dealing with one
        print("dealing with 1 scenario")
        boxes = []
        labels = []
        for key in plot_dict:
            #define_box_properties(ax, 
            bp1 =  ax.boxplot(plot_dict[key],
                              patch_artist=True, 
                              positions=np.array(np.arange(len(plot_dict[key])))*2.0, boxprops=dict(color='b'))
            boxes.append(bp1)
            labels.append(key)
                               
        ax.set_xticks(np.arange(0, len(ticks) * 2, 2), ticks)
        ax.set_ylabel('Passage Duration (s)')
        ax.legend([box["boxes"][0] for box in boxes], labels, loc='upper right')
        
def get_scenarios_to_compare(scenario_list, params):
    scenarios = []
    if(len(scenario_list) > 0):
        for s in scenario_list:
            scenario = read_scenario_from_json_file(params, s)
            #result = asyncio.run(compute_passage_and_normalise_for_a_run(scenario['runs'], params))
            result =  compute_passage_and_normalise_for_a_run_sync(scenario["runs"], params)
            scenario["consolidated_scenario_data"] = consolidate_runs_for_scenario(scenario, params)
            scenarios.append(scenario)
    return scenarios

def create_pressure_plot(scenario_data, deployment, fig, params):
    fig.clear()
    ax = fig.subplots()
    ax.set_title(deployment["name"])

    if(params.get_parameter("toggle_accleration")):
        if('a_mag_hig' in deployment):
            ax.plot(deployment['x_t_hig'], deployment['a_mag_hig'], color="red", linewidth=2, picker=False, alpha=0.6, label="Acceleration Magntidue (g)")
        elif("a_mag" in  deployment):
            print(deployment["x_t"])
            ax.plot(deployment['x_t'], deployment['a_mag'], color="black", linewidth=2, picker=False, alpha=0.8, label="Acceleration Magntidue (g)")
            ax.set_ylabel('Acceleration Magntidue (g)')
            ax.legend(loc='upper left')
        
    ax2 = ax.twinx()

    if(params.get_parameter("toggle_pressure")):
        ax2.plot(deployment['x_t'], deployment['y_p'], color="blue", linewidth=2, picker=True,  pickradius=1, label="Pressure (mbar)")
        if "pressure_roi" in deployment:
            labels = []
            indexes = []
            values = []

            # if it has been saved
            for key, value in deployment["pressure_roi"].items():
                labels.append(key)
                indexes.append(deployment['x_t'][value[0]])
                values.append(value[1])
            
            for key, value in scenario_data.get_pressure_roi().items():
                labels.append(key)
                indexes.append(deployment['x_t'][value[0]])
                values.append(value[1])

            ax2.scatter(indexes, values)
            for idx,l in enumerate(labels):
                ax2.annotate(l,(indexes[idx],values[idx]) )

        if "is_faulty" in deployment and deployment["is_faulty"] == True:
            ax2.text(0.5, 0.95, 'Faulty Deployment', ha='center', va='top', transform=ax.transAxes,  
            color='red', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    ax.set_xlabel('Time (s)')
    ax2.set_ylabel('Pressure (mbar)')
    ax2.yaxis.tick_right()
    ax2.legend(loc='upper right')

    ax.grid(True)

## Compute passage and normalise the data 
def compute_passage_durations(deployment_roi, sampling_frequency):
    injection_to_nadir_duration = (deployment_roi["Nadir"][0] - deployment_roi["Injection"][0]) / sampling_frequency
    nadir_to_tailwater_duration = (deployment_roi["Tailwater"][0] - deployment_roi["Nadir"][0]) / sampling_frequency
    passage_duration = (deployment_roi["Tailwater"][0] - deployment_roi["Injection"][0]) / sampling_frequency
    return {
        "injection_to_nadir_duration":injection_to_nadir_duration,
        "nadir_to_tailwater_duration":nadir_to_tailwater_duration,
        "passage_duration":passage_duration
        
    }

#params.get_parameter('resample_N')
def normalise_complete_deployment_dataset(deployment, N):

    # resample pressure
    y_p_resampled = resample(deployment["y_p"], N)

    # resample a_mag
    if "a_mag" in deployment:
        a_mag_resampled = resample(deployment["a_mag"], N)

    # resample time axis
    x_t_resampled = resample(deployment["x_t"], N)

    print(x_t_resampled)

    # hig 
    #if "x_t_hig" in  deployment:
    #    x_t_hig_resampled = resample(deployment["x_t_hig"], N)
    
    normalised_data = {
        "x_t_norm" : x_t_resampled,
        "y_p_resampled" : y_p_resampled,
        "a_mag_resampled": a_mag_resampled
    }
    
    return normalised_data

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
    size_post = idx_stop_post - (idx_start_post+1)
    #print("size post", size_post)
    ts_post = np.arange(0, size_post+1)/(2*size_post)+0.5 # this is empty
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
    

    # need to add accel_mag between injection and tailwater
    i_t_a_mag = deployment['a_mag'][idx_start:idx_stop_post+1]
    a_mag_resampled = resample(i_t_a_mag, int(N))
    print("length of resampled", len(a_mag_resampled), len(np.concatenate((i_to_n_resampled, n_to_t_resampled))))

    normalised_data = {
        'ts_pre':new_ts_pre,
        'i_to_n_resampled': i_to_n_resampled,
        'ts_post':new_ts_post,
        'n_to_t_resampled':n_to_t_resampled,
        "x_t_norm" : np.concatenate((new_ts_pre,new_ts_post)),
        "y_p_resampled" : np.concatenate((i_to_n_resampled, n_to_t_resampled)),
        "a_mag_resampled": a_mag_resampled,
    }
    
    return normalised_data

#async def compute_passage_and_normalise_for_a_deployment(deployment, params):
#    print("computing only passasge durations")
#    print(deployment["pressure_roi"],  flush=True)
#    deployment["passage_durations"] = compute_passage_durations(deployment['pressure_roi'], params.get_parameter('fs'))
#    deployment['normalised_data'] = normalise_deployment_data(deployment, params.get_parameter('resample_N'))

def compute_passage_and_normalise_for_a_deployment_sync(deployment, params):
    print("computing only passasge durations")
    deployment["passage_durations"] = compute_passage_durations(deployment['pressure_roi'], params.get_parameter('fs'))
    deployment['normalised_data'] = normalise_deployment_data(deployment, params.get_parameter('resample_N')) 

# assumes all deployments in the run are complete
# this is aysnc but for a demo does not need to be
#async def compute_passage_and_normalise_for_a_run(runs, params):
#    deployment_list = []
#    for r in runs:
#        print("computing passage durations and normalising")
#        for d in r['deployments']:

            # only include non faulty deployments
#            if(d["is_faulty"] == False):
#                deployment_list.append(compute_passage_and_normalise_for_a_deployment(d, params))
#        await asyncio.gather(*deployment_list)   
#    return "run"

def compute_passage_and_normalise_for_a_run_sync(runs, params):
    for r in runs:
        print("computing passage durations and normalising")
        for d in r['deployments']:
            # only include non faulty deployments
            if(d["is_faulty"] == False):
                res = compute_passage_and_normalise_for_a_deployment_sync(d, params)
    return "run"

def normalise_deployments_for_runs(runs, params):
    normalised_runs = []
    for r in runs:
        _r = {
            "name": r["name"],
            "deployments" : []
        }
        for d in r['deployments']:
            # only include non faulty deployments
            if(d["is_faulty"] == False):
                #res = normalise_complete_deployment_dataset(d, params.get_parameter('resample_N'))
                res = normalise_deployment_data(d, params.get_parameter('resample_N'))
                _d = {
                    "name": d["name"],
                    "norm_data": res
                }
                _r["deployments"].append(_d)
        normalised_runs.append(_r)
    return normalised_runs



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
        if(d["is_faulty"] == False):
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
        if(r["labeled"] == True):
            consolidated_run_data = consolidate_deployments(r['deployments'], params, params.get_parameter("h_min"), params.get_parameter("h_max"))

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
    if(len(data)> 1):
        std = statistics.stdev(data)
    else:
        std = 0
    
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