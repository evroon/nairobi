import csv
import numpy as np
import matplotlib.pyplot as plt

flight_info = np.genfromtxt('flight_info.csv', delimiter=';')[1:, 7]
bays = ['20','19','18','17','16','15','14','13','12','11','10','9','8','7','6','5','4L','4R','3C','3B','3A','2C','2B','2A','J1','J2A','J2B','J3A','J3B','J4A','J4B','J5','J6','J7','J8','J9','H1','H2','H3','H4','H5','H6']

fig, gnt = plt.subplots() 
gnt.set_ylim(0, len(bays))
gnt.set_xlim(0, 24)

gnt.set_xlabel('Time') 
gnt.set_ylabel('Bay') 

gnt.set_yticks(np.arange(len(bays)) + 0.5)
gnt.set_yticklabels(bays)
gnt.grid(True) 

# Plot Gantt diagram
for i, eta in enumerate(flight_info):
    gnt.broken_barh([(eta, 1)], (i%len(bays), 1), facecolors =('tab:blue'))

plt.show()