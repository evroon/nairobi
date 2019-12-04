import numpy as np

bays = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4L', '4R', '3C', '3B', '3A',
        '2C', '2B', '2A', 'J1', 'J2A', 'J2B', 'J3A', 'J3B', 'J4A', 'J4B', 'J5', 'J6', 'J7', 'J8', 'J9', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']

gates = np.arange(1, 24)

dataset = '02_06_2015'
dataset = '05_07_2015'

buffer = 15 # minutes

data_path = 'data/' + dataset + '/'
results_path = data_path + '/results/'
success = False

try:
    airline_preferences     = np.genfromtxt('data/general/airline_preferences.csv', delimiter=';', dtype="|U16")
    bay_compliance          = np.genfromtxt('data/general/bay_compliance.csv',      delimiter=';')
    fuelling_availability   = np.genfromtxt('data/general/fuelling_availability.csv', delimiter=';')
    walking_distance        = np.genfromtxt('data/general/walking_distance.csv', delimiter=';')
    flight_info_float       = np.genfromtxt(data_path + 'flights_processed.csv', delimiter=';')
    flight_info_text        = np.genfromtxt(data_path + 'flights_processed.csv', delimiter=';', dtype="|U16")
    
    success = True
except Exception as e:
    print('Could not open data file: ' + str(e))

if success:
    pax = flight_info_float[1:, 10]
    eta = flight_info_float[1:, 3]
    etd = flight_info_float[1:, 7]
    flight_count = len(pax)

    eta = np.maximum(eta, 0.0)
    etd = np.minimum(etd, 23 + 59 / 60)

    eta -= buffer / 60.0
    etd += buffer / 60.0

    flight_types = flight_info_text[1:, 0]
    arrival_flights = flight_info_text[1:, 1]
    departure_flights = flight_info_text[1:, 5]
    ac_class = flight_info_text[1:, 9]


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

def bay_supports_fuelling(bay):
    bay_index = bays.index(bay)
    return bool(fuelling_availability[bay_index + 1, 1])

def aircraft_has_to_be_fueled(aircraft):
    return flight_types[aircraft] in ['Full', 'Dep']

def get_walking_distance(bay):
    bay_index = bays.index(bay)
    return walking_distance[bay_index + 1, 1]