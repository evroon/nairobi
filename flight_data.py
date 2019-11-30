import csv
import numpy as np
import matplotlib.pyplot as plt
import model

A = ['AT4', 'AT7', 'Q400']
B = ['B733', 'E70']
C = ['E90']
D = ['B737', 'B738', 'A320']
E = ['B73J']
F = ['B787', 'B788', 'A330', 'B767']
G = ['B772', 'B773']
H = ['B747']

types = {
    'Q40': 'A',
    'AT4': 'A',
    'AT7': 'A',
    'CRJ': 'A',
    '733': 'B',
    'E70': 'B',
    'E90': 'C',
    '737': 'D',
    '738': 'D',
    '320': 'D',
    '73J': 'E',
    '787': 'F',
    '788': 'F',
    '330': 'F',
    '332': 'F',
    '767': 'F',
    '772': 'G',
    '773': 'G',
    '747': 'H',
}

passengers = {
    'Q40': 40,
    'AT4': 52,
    'AT7': 72,
    'CRJ': 90,
    '733': 126,
    'E70': 72,
    'E90': 96,
    '737': 126,
    '73J': 126,
    '738': 162,
    '320': 150,
    '767': 200,
    '787': 234,
    '788': 234,
    '332': 233,
    '330': 268,
    '772': 302,
    '773': 385,
    '747': 429,
}


def process_data(filename):
    '''
    Add two columns with aircraft class and passenger data
    Set the ETA and ETD correctly
    '''

    np.random.seed(2)
    data = np.genfromtxt(filename, delimiter=';', dtype="|U16")

    first_index = np.asarray([0])
    data_length = data.shape[0]
    indices = np.append(first_index, np.random.randint(1, data_length, int(data_length * 0.7) - 1))
    data = data[indices, :]

    result = np.zeros((data.shape[0], data.shape[1] + 2), dtype="|U16")
    result[:, :-2] = data

    for ac in range(1, result.shape[0]):
        result[ac, -2] = types[result[ac, -3]]
        result[ac, -1] = passengers[result[ac, -3]]
        result[ac, 3] = result[ac, 3].replace(':', '.')
        result[ac, 7] = result[ac, 7].replace(':', '.')

        if result[ac, 0] == 'Park':
            result[ac, -1] = 0.0

        eta = float(result[ac, 3])
        etd = float(result[ac, 7])

        if etd < eta:
            result[ac, 7] = 24.0
            etd = float(result[ac, 7])
        
        # Multiply minutes by 10 / 6 in order to get correct decimals
        # (in range 0.0 to 1.0 instead of 0.0 to 0.6)
        result[ac, 3] = '{:.2f}'.format(eta // 1 + (eta % 1) * 10.0 / 6.0)
        result[ac, 7] = '{:.2f}'.format(etd // 1 + (etd % 1) * 10.0 / 6.0)

    result[0, -2] = 'Class'
    result[0, -1] = 'Pax'
    np.savetxt(filename[:-4] + '_processed.csv', result, delimiter=';', fmt='%s')


process_data('data/' + model.dataset + '/flights.csv')
