import numpy as np
import csv
from io import StringIO

bays = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4L', '4R', '3C', '3B', '3A',
        '2C', '2B', '2A', 'J1', 'J2A', 'J2B', 'J3A', 'J3B', 'J4A', 'J4B', 'J5', 'J6', 'J7', 'J8', 'J9', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']

airline_preferences = np.genfromtxt('data/airline_preferences.csv', delimiter=';', dtype="|U5")
bay_compliance      = np.genfromtxt('data/bay_compliance.csv',      delimiter=';')
flight_info_float   = np.genfromtxt('data/flight_info.csv',         delimiter=';')
flight_info_text    = np.genfromtxt('data/flight_info.csv',         delimiter=';', dtype="|U5")

pax = flight_info_float[1:, 3]
eta = flight_info_float[1:, 7]
etd = flight_info_float[1:, 10]

arrival_flights = flight_info_text[1:, 9]
departure_flights = flight_info_text[1:, 12]
ac_class = flight_info_text[1:, 2]

flight_count = len(eta)

# Check whether an aircraft can park at a certain bay,
# where bay is the name of a bay (not an index) and
# where flight is the index of a flight
def ac_can_park_at_bay(flight, bay):
    bay_index = bays.index(bay)
    ac_type = ac_class[flight]
    ac_type_index = ord(ac_type) - ord('A')
    
    return bool(bay_compliance[bay_index + 2, ac_type_index + 1])

# Check whether an aircraft is obeying the preference of its airline,
# where bay is the name of a bay (not an index) and
# where flight is the index of a flight
def flight_has_preference(flight, bay):
    dep = departure_flights[flight]
    preference_index = np.argwhere(airline_preferences[:, 0] == dep)

    if len(preference_index) < 1:
        return 0

    preferred_bay = airline_preferences[preference_index[0][0], 2]
    return int(bay == preferred_bay)