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


def calc_overlap_matrix():
    if os.path.isfile('data/overlap_matrix.csv'):
        print('Loaded overlap_matrix.csv from cache')
        return np.loadtxt('data/overlap_matrix.csv', delimiter=';')

    eta, etd, flight_count = model.get_flight_info()
    C = np.zeros((flight_count, flight_count), dtype=int)

    for i in range(flight_count):
        for j in range(flight_count):
            C[i, j] = eta[i] < etd[j] and eta[i] > eta[j]

    np.savetxt('data/overlap_matrix.csv', C, delimiter=';', fmt='%s')
    return C


def write_to_file():
    f = open('results/problem.lp', 'w+')

    C = calc_overlap_matrix()
    C = np.reshape(C, (50, 50))
    flight_count = np.shape(C)[0]

    result = 'max: 0;\n'

    # Time slot constraints: Xik + Xjk <= 1
    for k in model.bays:
        for i in range(flight_count):
            for j in range(flight_count):
                if C[i, j] == 1:
                    result += 'X_{i}_{k} + X_{j}_{k} <= 1;\n'.format(i=i, j=j, k=k)

    # Single bay constraint: sum of Xik is equal to 1 for all k
    for i in range(flight_count):
        for k in model.bays[:-1]:
            result += 'X_{i}_{k} + '.format(i=i, k=k)

        result += 'X_{i}_{k} = 1;\n'.format(i=i, k=model.bays[-1])

    # Xik is binary
    result += 'bin'
    for i in range(flight_count):
        for k in model.bays:
            result += ' X_{i}_{k}'.format(i=i, k=k)

    result += ';\n'

    f.write(result)
    f.close()


def solve():
    print('Solving...')
    with open("results/lp_result.txt", "w") as f:
        result = subprocess.call('lp_solve results/problem.lp', shell=True, stdout=f)

    return result


def process_results():
    with open("results/lp_result.txt", "r") as f:
        x = re.findall("X.* .*1", f.read())
        assignments = np.zeros((len(x), 2), dtype=int)

        for a in x:
            x = a.split('_')
            flight = int(x[1])
            bay = x[2][:-1].strip()
            bay_index = model.bays.index(bay)

            print('Flight {} is assigned to bay {}'.format(flight, bay))
            assignments[flight] = [flight, bay_index]
    
    np.savetxt('results/assignment_result.csv', assignments, delimiter=';', fmt='%s')


write_to_file()
solve()
process_results()