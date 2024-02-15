def create_fig_7_pressure_and_rpc_plots(scenarios, fig):
    fig.clear()
    plot_dict = {}
    ax = fig.subplots(2,2)
    ax[0][0], ax[0][1] = create_fig_7_pressure_plots(scenarios, ax[0][0], ax[0][1])
    ax[1][0], ax[1][1] = create_fig_7_rpc_plots(scenarios, ax[1][0], ax[1][1])

def create_fig_7_rpc_plots(scenarios, ax1, ax2):
     ## BOX PLOTS
    plot_dict = {}
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