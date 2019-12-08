import csv
import numpy as np
import matplotlib.pyplot as plt
import model
from collections import OrderedDict

plt.rcParams.update({'font.size': 16})

eta, etd, flight_count, arrival_flights = model.eta, model.etd, model.flight_count, model.arrival_flights

def setup_gantt_plot():
    fig, gnt = plt.subplots(figsize=(18, 16))
    gnt.set_ylim(0, len(model.bays))
    gnt.set_xlim(0, 24)

    gnt.set_xlabel('Time')
    gnt.set_ylabel('Bay')

    gnt.set_yticks(np.arange(len(model.bays)) + 0.5)
    gnt.set_yticklabels(model.bays)

    time_ticks = [str(x) for x in np.arange(0, 24)]
    gnt.set_xticks(np.arange(0, 24))
    gnt.set_xticklabels(time_ticks)

    gnt.yaxis.grid()

    cmap = plt.cm.get_cmap('winter_r')    
    return gnt, cmap

def plot_bay_assignment():
    gnt, cmap = setup_gantt_plot()
    assignments = np.genfromtxt(model.results_path + 'bay_assignment_result.csv', delimiter=';')

    if len(assignments) < 1:
        print('Problem is infeasible!')
        quit()

    # Plot Gantt diagram
    for i, _ in enumerate(eta):
        _, bay = assignments[i]
        ac_class = model.ac_class[i]
        rgba = cmap((ord(ac_class) - ord('A')) / (ord('G') - ord('A')))

        arrival = eta[i] + model.buffer / 60.0
        departure = etd[i] - model.buffer / 60.0
        stay_period = departure - arrival

        gnt.broken_barh([(arrival, stay_period)], (bay, 1), facecolors=rgba, label=ac_class)

    handles, labels = plt.gca().get_legend_handles_labels()
    keys, values = [], []
    dict = OrderedDict(zip(labels, handles))

    for i in sorted(dict):
        keys.append(i)
        values.append(dict[i])

    plt.legend(values, keys, loc='upper left')
    plt.savefig(model.results_path + 'schedule.png', bbox_inches='tight')

def plot_gate_assignment():
    gnt, cmap = setup_gantt_plot()
    assignments = np.genfromtxt(model.results_path + 'gate_assignment_result.csv', delimiter=';')

plot_bay_assignment()
plot_gate_assignment()
plt.show()
