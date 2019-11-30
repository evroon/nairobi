import csv
import numpy as np
import matplotlib.pyplot as plt
import model


eta, etd, flight_count = model.get_flight_info()

fig, gnt = plt.subplots()
gnt.set_ylim(0, len(model.bays))
gnt.set_xlim(0, 24)

gnt.set_xlabel('Time')
gnt.set_ylabel('Bay')

gnt.set_yticks(np.arange(len(model.bays)) + 0.5)
gnt.set_yticklabels(model.bays)
gnt.grid(True)

cmap = plt.cm.get_cmap('Spectral')

assignments = np.genfromtxt('results/assignment_result.csv', delimiter=';')

# Plot Gantt diagram
for i, _ in enumerate(eta):
    flight, bay = assignments[i]
    rgba = cmap(i / flight_count)
    gnt.broken_barh([(eta[i], etd[i] - eta[i])], (bay, 1), facecolors=rgba, label=flight)

plt.legend()
plt.show()
