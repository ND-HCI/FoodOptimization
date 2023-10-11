# imports the OptimizerConstraints class from Optimizer folder
from OptimizerConstraints import OptimizerConstraints
import re
import logging
from mip import Model, xsum, maximize, minimize, BINARY, INTEGER, OptimizationStatus
import pandas as pd
from typing import Dict
import json
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
# These lines check if the parent directory is in the Python path (the list of directories where the interpreter looks for modules to import)
if parent not in sys.path:
    # If the parent directory is not in the path, it is appended to the path, allowing for the import of custom modules located in the parent directory.
    sys.path.append(parent)


class NutOptimizer:

    # Takes DataFrame of data to be used by the Optimizer and Optimizer constraints as a dictionary
    def __init__(self, data: pd.DataFrame, constraints: Dict[str, OptimizerConstraints] = dict()):
        self.data = data.copy()
        self.constraints = constraints

    # Returns the name and the key-value pairs of the constaints into a single string
    def __repr__(self):
        output = []
        for _, constraint in self.constraints.items():
            output.append(str(constraint))
        return '\n'.join(output)

    # Reads constraints from a JSON file and creates dictionary
    # Parameters: filepath = string representing the path to the JSON file containing the constraints;
    # "append" = boolean flag indicating whether to append the loaded constraints to the existing constraints (True) or to replace the existing constraints with the loaded constraints (False)
    def load_constraints_json(self, filepath: str, append=False):
        if not append:
            self.constraints = {}  # if append = False
        with open(filepath, 'r') as fp:
            constraints = json.load(fp)  # python dictionary
        for constraint, vals in constraints.items():
            # print(constraint)
            # print(vals)
            self.constraints[constraint] = OptimizerConstraints(constraint, vals)

    # optimization_col = string representing the name of the column to be optimized; var_type = binary v. integer optimization; optimization_type = min/max
    # verbose = boolean controlling whether to print progress messages during optimization; timeout = integer representing the maximum time allowed for optimization process
    def optimize_all(self, optimization_cols: list, weights: list, var_type='INTEGER', optimization_type='min', verbose: bool = True, timeout: int = 300):
        if var_type.lower() not in ['binary', 'integer']:
            raise ValueError("var_type must be 'binary' or 'integer'")
        if optimization_type.lower() not in ['max', 'min']:
            raise ValueError("optimization_type must be 'min' or 'max'")
        for constraint in self.constraints:
            self.optimize_one(constraint, optimization_cols, weights, var_type, 
                              optimization_type, verbose=verbose, timeout=timeout)


    # # Sets up Optimization Model, adds variables, sets objective function, adds constraints limits, and updates data with results from optimization
    def optimize_one(self, constraint_name: str, optimization_cols: list, weights: list, var_type='INTEGER', optimization_type='min', verbose: bool = True, timeout: int = 300):
        #Vvalidate that the var_type and optimization_type inputs are valid (either 'binary' or 'integer' for var_type, and 'min' or 'max' for optimization_type). If not, a ValueError is raised.
        if var_type.lower() not in ['binary', 'integer']:
            raise ValueError("var_type must be 'binary' or 'integer'")
        if optimization_type.lower() not in ['max', 'min']:
            raise ValueError("optimization_type must be 'min' or 'max'")
        #retrieves the constraints for the specified constraint name.
        constraints = self.constraints[constraint_name]
        num_items = range(self.data.shape[0])

        #Creating new MIP model using constraints name
        m = Model(constraints.get_name())
        m.verbose = 0

        #Add variable x to the model for binary/integer
        if var_type.lower() == 'binary':
            x = [m.add_var(var_type=BINARY) for _ in num_items]
        elif var_type.lower() == 'integer':
            x = [m.add_var(var_type=INTEGER) for _ in num_items]

    #     #Objective function
        if optimization_type.lower() == 'max':
            m.objective = maximize(
                sum(weight * xsum(x[i] * self.data[col][i] for i in num_items) for weight, col in zip(weights, optimization_cols)))
        elif optimization_type.lower() == 'min':
            m.objective = minimize(
                sum(weight * xsum(x[i] * self.data[col][i] for i in num_items) for weight, col in zip(weights, optimization_cols)))

        #loops over each key 
        #if the constraint key is present in the data columns. If not, a ValueError is raised.
        for key in constraints:
            if key not in self.data.columns:
                raise ValueError(f"{key} in constraints but not in data")
            min_val = constraints[key].get('min')
            max_val = constraints[key].get('max')

            if min_val is not None:   #checks if min value constraint is specified
                m += xsum(x[i] * self.data[key][i]  # 
                          for i in num_items) >= min_val
            if max_val is not None:   #checks if max value constraint is specified
                m += xsum(x[i] * self.data[key][i]
                          for i in num_items) <= max_val

        m.optimize(max_seconds=timeout)

        if m.status == OptimizationStatus.FEASIBLE:
            logging.info(f"Suboptimal solution found for {constraint_name}")
        if m.status == OptimizationStatus.INFEASIBLE:
            logging.info(f"Solution infeasible for {constraint_name}")

        self.data[f"Selected_{constraint_name}"] = [i.x for i in m.vars]
        if verbose:
            print(f"{constraint_name}\nOptimal {optimization_col}: {self.get_one_optimal_value(constraint_name, optimization_col)} \n {self.get_one_result(constraint_name)}")


    def get_all_results(self):
        res = {}
        for constraint in self.constraints:
            res[constraint] = self.get_one_result(constraint)
        return res

    def get_one_result(self, constraint: str):
        cols = self.data.columns
        ss = re.compile("Selected_*")
        new_cols = []
        for col in cols:
            if ss.match(col) is None:
                new_cols.append(col)
        new_cols.append(f"Selected_{constraint}")

        return self.data[self.data[f"Selected_{constraint}"] >= 0.99][new_cols].rename(columns={f"Selected_{constraint}": "Amount"})

    def get_all_optimal_values(self, optimzation_col: str):
        res = {}
        for constraint in self.constraints:
            res[constraint] = self.get_one_optimal_value(
                constraint, optimzation_col)
        return res

    def get_one_optimal_value(self, constraint: str, optimzation_col: str):
        vals = self.data.loc[self.data[f"Selected_{constraint}"] >= 0.99, optimzation_col] * \
            self.data.loc[self.data[f"Selected_{constraint}"]
                          >= 0.99, f"Selected_{constraint}"]
        return sum(vals)

    def set_data(self, data: pd.DataFrame):
        self.data = data

    def set_constraints(self, constraints: Dict[str, OptimizerConstraints]):
        self.constraints = constraints

    def get_data(self):
        return self.data

    def get_constraints(self):
        return self.constraints

    def get_models(self):
        return list(self.constraints.keys())

    def remove_model(self, name: str):
        del self.constraints[name]

    def update_constraint(self, name: str, constraint: str, type: str, val):
        self.constraints[name].update_constraint(constraint, type, val)

    def remove_constraint(self, name: str, constraint: str, type: str):
        self.constraints[name].remove_constraint(constraint, type)

    # Add method to write constraints to json
    def dump_constraints_json(self, filepath: str):
        constraints = {}
        for const in self.constraints:
            constraints[const] = self.constraints[const].get_constraints_dict()
        with open(filepath, 'w') as fp:
            json.dump(constraints, fp, indent=4)


def test():
    dat = pd.read_csv('test_data.csv')
    # name = 'Test'
    # test_constraints = {'Vitamin A': {'min': 5, 'max': 10}, 'Vitamin B': {'min': 0, 'max': 100}, 'Vitamin C': {'min': 11, 'max': 25}}
    # test_class = OptimizerConstraints(name, test_constraints)
    testOptimizer = NutOptimizer(dat)

    # Example of loading json constraints
    testOptimizer.load_constraints_json("./test_data_consts.json")
    print(testOptimizer)

    testOptimizer.dump_constraints_json("./dumpetydump.json")
    testOptimizer.optimize_all("v", optimization_type='max', var_type='binary', verbose=False)
    print("Optimal Values: ")
    print(testOptimizer.get_all_optimal_values("v"))
    print("")
    print("All Results: ")
    print(testOptimizer.get_all_results())
    print("")
    print("Get Models: ")
    print(testOptimizer.get_models())


if __name__ == '__main__':
    test()