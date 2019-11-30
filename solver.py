import numpy as np
import subprocess
import os
import re
import model


'''
Decision variables:
Xik: 1 if flight i is assigned to bay k, and 0 otherwise.

Constants:
Overlap matrix Cij: 1 if aircraft i and j are at the airport at the same time.
'''

eta, etd, flight_count, arrival_flights, bays = model.eta, model.etd, model.flight_count, model.arrival_flights, model.bays

def calc_overlap_matrix(use_cache = False):
    path = model.data_path + 'overlap_matrix.csv'
    if use_cache and os.path.isfile(path):
        print('Loaded overlap_matrix.csv from cache')
        return np.loadtxt(path, delimiter=';')

    C = np.zeros((flight_count, flight_count), dtype=int)

    for i in range(flight_count):
        for j in range(flight_count):
            C[i, j] = (eta[i] <= etd[j] and eta[i] >= eta[j]) or \
                      (etd[i] <= etd[j] and etd[i] >= eta[j]) or \
                      (etd[i] >= etd[j] and eta[i] <= eta[j])

    np.savetxt(path, C, delimiter=';', fmt='%s')
    return C


def write_to_file():
    f = open(model.results_path + 'problem.lp', 'w+')

    C = calc_overlap_matrix()
    flight_count = np.shape(C)[0]

    # Objective function
    result = 'max: '
    objective_elements = []
    for k in bays:
        for i in range(flight_count):
            if model.flight_has_preference(i, k):
                objective_elements.append('X_{i}_{k}'.format(i=i, k=k))

    result += ' + '.join(objective_elements) + ';\n'

    # Time slot constraints: Xik + Xjk <= 1, i != j
    for k in bays:
        for i in range(flight_count):
            for j in range(i + 1, flight_count):
                if C[i, j] == 1:
                    result += 'X_{i}_{k} + X_{j}_{k} <= 1;\n'.format(i=i, j=j, k=k)

    # Single bay constraint: sum of Xik is equal to 1 for all k corresponding to a suitable bay
    # Aircraft has to park somewhere
    for i in range(flight_count):
        constraint_elements = []

        for k in bays:
            if model.ac_can_park_at_bay(i, k):
                constraint_elements.append('X_{i}_{k}'.format(i=i, k=k))

        result += ' + '.join(constraint_elements) + ' = 1;\n'

    # Single bay constraint: sum of Xik is equal to 0 for all k corresponding to a unsuitable bay
    # Aircraft cannot park at unsuitable bays
    for i in range(flight_count):
        constraint_elements = []

        for k in bays:
            if not model.ac_can_park_at_bay(i, k):
                constraint_elements.append('X_{i}_{k}'.format(i=i, k=k))

        if len(constraint_elements) > 0:
            result += ' + '.join(constraint_elements) + ' = 0;\n'

    # Fueling availability constraint
    for i in range(flight_count):
        if model.aircraft_has_to_be_fueled(i):
            constraint_elements = []
            
            for k in bays:
                if model.bay_supports_fueling(k):
                    constraint_elements.append('X_{i}_{k}'.format(i=i, k=k))

            result += ' + '.join(constraint_elements) + ' = 1;\n'

    # Xik is binary
    result += 'bin '
    binary_variables = []
    for i in range(flight_count):
        for k in bays:
            binary_variables.append('X_{i}_{k}'.format(i=i, k=k))

    result += ', '.join(binary_variables) + ';\n'

    f.write(result)
    f.close()


def solve():
    print('Solving...')
    with open(model.results_path + 'lp_result.txt', 'w') as f:
        problem_path = model.results_path + 'problem.lp'
        result = subprocess.call('lp_solve {}'.format(problem_path), shell=True, stdout=f)

    return result


def process_results():
    with open(model.results_path + 'lp_result.txt', 'r') as f:
        x = re.findall("X.* .*1", f.read())
        assignments = np.zeros((len(x), 2), dtype=int)

        for a in x:
            x = a.split('_')
            flight = int(x[1])
            bay = x[2][:-1].strip()
            bay_index = bays.index(bay)            
            assignments[flight] = [flight, bay_index]
    
    np.savetxt(model.results_path + 'assignment_result.csv', assignments, delimiter=';', fmt='%s')


write_to_file()
solve()
process_results()
