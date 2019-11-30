import numpy as np
import csv
from io import StringIO

bays = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4L', '4R', '3C', '3B', '3A',
        '2C', '2B', '2A', 'J1', 'J2A', 'J2B', 'J3A', 'J3B', 'J4A', 'J4B', 'J5', 'J6', 'J7', 'J8', 'J9', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']

bay_compliance    = np.genfromtxt('data/bay_compliance.csv', delimiter=';')
flight_info_float = np.genfromtxt('data/flight_info.csv',    delimiter=';')
flight_info_text  = np.genfromtxt('data/flight_info.csv',    delimiter=';', dtype="|U5")

def get_basic_flight_info():
    eta = flight_info_float[1:, 7]
    etd = flight_info_float[1:, 10]
    flight_count = len(eta)
    return eta, etd, flight_count

def get_callsigns():
    return flight_info_text[1:, 9]

def get_ac_class():
    return flight_info_text[1:, 2]

# Check whether an aircraft/flight can park at a certain bay,
# where bay is the name of a bay (not an index)
def ac_can_park_at_bay(flight, bay):
    bay_index = bays.index(bay)
    ac_type = get_ac_class()[flight]
    ac_type_index = ord(ac_type) - ord('A')
    
    return bool(bay_compliance[bay_index + 2, ac_type_index + 1])
