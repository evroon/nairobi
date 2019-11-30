import csv
import numpy as np
import matplotlib.pyplot as plt
import model


eta, etd, flight_count, arrival_flights = model.eta, model.etd, model.flight_count, model.arrival_flights

fig, gnt = plt.subplots(figsize=(18, 16))
gnt.set_ylim(0, len(model.bays))
gnt.set_xlim(0, 24)

gnt.set_xlabel('Time')
gnt.set_ylabel('Bay')

gnt.set_yticks(np.arange(len(model.bays)) + 0.5)
gnt.set_yticklabels(model.bays)

time_ticks = [str(x) + ':00' for x in np.arange(0, 24)]
gnt.set_xticks(np.arange(0, 24))
gnt.set_xticklabels(time_ticks)

gnt.grid(True)

cmap = plt.cm.get_cmap('Spectral')

assignments = np.genfromtxt(model.results_path + 'assignment_result.csv', delimiter=';')

if len(assignments) < 1:
    print('Problem is infeasible!')
    quit()

# Plot Gantt diagram
for i, _ in enumerate(eta):
    _, bay = assignments[i]
    rgba = cmap(i / flight_count)
    gnt.broken_barh([(eta[i], etd[i] - eta[i])], (bay, 1), facecolors=rgba, label=arrival_flights[i])

# plt.legend(bbox_to_anchor=(1.08, 1.01))
plt.savefig('results/gantt.png', bbox_inches='tight')
plt.show()
