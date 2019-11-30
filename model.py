import numpy as np


bays = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '9', '8', '7', '6', '5', '4L', '4R', '3C', '3B', '3A',
        '2C', '2B', '2A', 'J1', 'J2A', 'J2B', 'J3A', 'J3B', 'J4A', 'J4B', 'J5', 'J6', 'J7', 'J8', 'J9', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']


def get_flight_info():
    flight_info = np.genfromtxt('data/flight_info.csv', delimiter=';')
    eta = flight_info[1:, 7]
    etd = flight_info[1:, 10]
    flight_count = np.shape(eta)[0]
    return eta, etd, flight_count

def get_callsigns():
    flight_info = np.genfromtxt('data/flight_info.csv', delimiter=';')
    return flight_info[1:, 10]