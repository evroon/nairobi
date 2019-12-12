import numpy as np
import subprocess
import os
import model


'''
Decision variables:
Xik: 1 if flight i is assigned to bay k, and 0 otherwise.

Constants:
Overlap matrix Cij: 1 if aircraft i and j are at the airport at the same time.
'''

eta, etd, flight_count, arrival_flights, bays, gates = model.eta, model.etd, model.flight_count, model.arrival_flights, model.bays, model.gates

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


def write_bay_assignment():
    f = open(model.results_path + 'bay_assignment.lp', 'w+')

    C = calc_overlap_matrix()
    flight_count = np.shape(C)[0]

    # Start objective function
    result = 'max: '
    objective_elements = []
    for k in bays:
        for i in range(flight_count):
            if model.flight_has_bay_preference(i, k):
                objective_elements.append('X_{i}_{k}'.format(i=i, k=k))

    result += ' + '.join(objective_elements)
    result += ' - '

    # Minimize passenger travel distance, use negative factors.
    objective_elements = []
    for k in bays:
        for i in range(flight_count):
            p = model.pax[i]
            d = model.get_walking_distance(k)

            if p * d > 0.0:
                objective_elements.append('{pd:.0f} X_{i}_{k}'.format(pd=p * d, i=i, k=k))

    result += ' - '.join(objective_elements) + ';\n'

    # Start constraints
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

    # Fuelling availability constraint
    for i in range(flight_count):
        if model.aircraft_has_to_be_fueled(i):
            constraint_elements = []
            
            for k in bays:
                if model.bay_supports_fuelling(k):
                    constraint_elements.append('X_{i}_{k}'.format(i=i, k=k))

            result += ' + '.join(constraint_elements) + ' = 1;\n'

    # 4L can only handle a wide body (higer than class D) if 4R is empty,
    # so the sum of all widebodies at 4L and all aircraft at 4R must be <= 1
    widebodies_4L = []
    for i in range(flight_count):
        if ord(model.ac_class[i]) - ord('D') > 0:
            widebodies_4L.append('X_{i}_4L'.format(i=i))

    any_4R = []
    for i in range(flight_count):
        any_4R.append('X_{i}_4R'.format(i=i))

    result += ' + '.join(widebodies_4L) + ' + ' + ' + '.join(any_4R) + ' <= 1;\n'

    # Xik is binary
    result += 'bin '
    binary_variables = []
    for i in range(flight_count):
        for k in bays:
            binary_variables.append('X_{i}_{k}'.format(i=i, k=k))

    result += ', '.join(binary_variables) + ';\n'

    f.write(result)
    f.close()

    
def write_gate_assignment():
    C = calc_overlap_matrix()

    with open(model.results_path + 'gate_assignment.lp', 'w+') as f:
        result = 'max: '

        # Objective function: maximize airline preferences.
        objective_elements = []
        for g in gates:
            for i in range(flight_count):
                if model.flight_has_gate_preference(i, g):
                    objective_elements.append('Y_{i}_{g}'.format(i=i, g=g))

        result += ' + '.join(objective_elements) + ' -'

        # Objective funcion: minimize multiple flights at same gate.
        objective_elements = []
        for g in gates:
            for i in range(model.flight_count):
                for j in range(model.flight_count):
                    objective_elements.append('k_{i}_{j}_{g}'.format(i=i, j=j, g=g))

        result += ' - '.join(objective_elements) + ';\n'

        # Constraint: Write variables k_g as a soft constraint.
        for g in gates:
            for i in range(model.flight_count):
                for j in range(model.flight_count):
                    if C[i, j] == 1:
                        result += 'Y_{i}_{g} + Y_{j}_{g} - k_{i}_{j}_{g} <= 1;\n'.format(i=i, j=j, g=g)

        # Constraint: flight must use exactly one gate.
        for i in range(model.flight_count):
            constraint_elements = []
            for g in gates:
                constraint_elements.append('Y_{i}_{g}'.format(i=i, g=g))
        
            result += ' + '.join(constraint_elements) + ' = 1;\n'

        # Yik is binary
        result += 'bin '
        binary_variables = []
        for i in range(flight_count):
            for g in gates:
                binary_variables.append('Y_{i}_{g}'.format(i=i, g=g))

        result += ', '.join(binary_variables) + ';\n'

        f.write(result)


def solve(filename, use_lpsolve):
    print('Solving {}...'.format(filename))
    with open(model.results_path + filename + '_result.txt', 'w') as f:
        problem_path = model.results_path + filename + '.lp'
        mps_path = model.results_path + filename + '.mps'

        if use_lpsolve:
            result = subprocess.call('lp_solve -f {} -wfmps {}'.format(problem_path, mps_path), shell=True, stdout=f)
        else:
            result = subprocess.call('lp_solve -parse_only {} -wfmps {}'.format(problem_path, mps_path), shell=True, stdout=f)

    return result


write_bay_assignment()
write_gate_assignment()
solve('bay_assignment', False)
solve('gate_assignment', True)