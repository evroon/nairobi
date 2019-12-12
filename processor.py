import numpy as np
import model
import re

bays, gates = model.bays, model.gates


def process_bay_assignment_cplex():
    with open(model.results_path + 'bay_assignment.sol', 'r') as f:
        expression = '<variable name="(.*)" index="(.*)" value="1"/>'
        vars = re.findall(expression, f.read())
        assignments = np.zeros((len(vars), 2), dtype=int)

        for a in vars:
            x = a[0].split('_')
            flight = int(x[1])
            bay = x[2].strip()
            bay_index = bays.index(bay)            
            assignments[flight] = [flight, bay_index]
    
    np.savetxt(model.results_path + 'bay_assignment_result.csv', assignments, delimiter=';', fmt='%s')


def process_gate_assignment_lpsolve():
    with open(model.results_path + 'gate_assignment_result.txt', 'r') as f:
        expression = 'Y_(.*)_(.*)[" "]{10,}1'
        vars = re.findall(expression, f.read())
        assignments = np.zeros((len(vars), 2), dtype=int)

        for a in vars:
            flight = int(a[0])
            gate = a[1].strip()
            assignments[flight] = [flight, gate]
    
    np.savetxt(model.results_path + 'gate_assignment_result.csv', assignments, delimiter=';', fmt='%s')
    
process_bay_assignment_cplex()
process_gate_assignment_lpsolve()
