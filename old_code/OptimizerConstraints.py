import json

class OptimizerConstraints:
    def __init__(self, name: str, constraints: dict = {}):
        self.name = name
        self._check_typing_of_constraints(constraints)
        self.constraints = constraints

    # Checks the data type of the values in the constraints dictionary and rasies a TypeError if the values are not dictionaries
    def _check_typing_of_constraints(self, constraints):
        for key, val in constraints.items():
            if not isinstance(val, dict):
                raise TypeError(
                    f"Constraints must be dictionary not {type(val)}: {key}: {val}")

    # Returns the name and the key-value pairs of the constaints into a single string
    def __repr__(self):
        output = [f'{self.name}:']
        for i in self.constraints:
            # appends new string element to the output for each key-value pair in the constraints dictionary
            output.append(f'{i}: {self.constraints[i]}')
        return '\n\t'.join(output)

    # Allows the object to be interable, meaning it can be looped over using a 'for' loop for example
    # For example the code below will print each key from the constraints dictionary
        # for constraint_key in opt_constraints:
        # print(constraint_key)
    def __iter__(self):
        yield from self.constraints

    # Checks if a specified item is contained in the object
    # Argument takes "name", which is the item you want to check for containment
    # Ex: If "name" is a key in the 'constraints' dictionary the expression will evaluate to True, otherwise False
    def __contains__(self, name):
        return name in self.constraints

    # Checks if the name is in the constraints dictionary and returns corresponding value of the key
    def __getitem__(self, name):
        if name in self.constraints:
            return self.constraints[name]
        else:
            raise KeyError(f'{name} not in Constraints')

    # Takes the parameters 'name', which is the key you want to set or modify and 'val' which is the value you want to associate with the key
    # This allows us to modify the constraint values
    def __setitem__(self, name, val):
        if not isinstance(val, dict):
            raise TypeError("Constraints must be dictionary")
        self.constraints[name] = val

    # Returns the number of elements in the constraints dictionary
    def __len__(self):
        return len(self.constraints)

    # Takes in 'name' parameter and deletes values from constraint dictonary
    def __delitem__(self, name):
        if name in self.constraints:
            del self.constraints[name]
        else:
            raise KeyError(f'{name} not in Constraints')

    # Updates the constraint value (minimum or maximum) for a given constraint name
    # Parameters: "name": constraint name you want to update;  "type": whether you want to update the min or max value;  "val": the new value for the min/max constraint
    def update_constraint(self, name, type, val):
        assert type in ['min', 'max']
        if name not in self.constraints:
            self.constraints[name] = {type: val}
        else:
            self.constraints[name][type] = val

    # Removes constraint value min/max for a given constraint name in the constraints dictionary
    def remove_constraint(self, name, type):
        del self.constraints[name][type]

    # Returns name of the OptimizerConstraints object
    def get_name(self):
        return self.name

    # Sets or updates the name of the OptimizerConstraints object
    # Input name parameter to update name
    def set_name(self, name: str):
        self.name = name

    # Returns the constraints in a dictonary
    def get_constraints_dict(self):
        return self.constraints

    # Update the constraint dictionary
    # Input dictonary of new constraints
    def set_constraints_dict(self, constraints: dict):
        self.constraints = constraints

    # Reads constraint values from a key in JSON file and loads them into the constraints dicionary
    def load_constraints_json(self, filepath: str, name: str):
        with open(filepath, 'r') as fp:
            constraints = json.load(fp)
        assert name in constraints.keys()
        self.constraints = constraints[name]

    # Write the constraints dictionary to a json file using the object's name as a key
    def dump_constraints_json(self, filepath: str):
        with open(filepath, 'w') as fp:
            json.dump({self.name: self.constraints}, fp, indent=4)


def test():
    name = 'Test'
    test_constraints = {'Vitamin A': {'min': 5, 'max': 10}, 'Vitamin B': {
        'min': 0, 'max': 100}, 'Vitamin C': {'min': 11, 'max': 25}}
    test_class = OptimizerConstraints(name, test_constraints)
    # print(test_class)
    # test_class.update_constraint('Vitamin D', 'min', 50)
    # print(test_class)
    # print(test_class.get_name())

    # Example of interation over constraint dictionary
    for constraint_key in test_constraints:
        print(constraint_key)

    # Example checking if name is present in dictionary
    if 'Vitamin D' in test_constraints:
        print('Constraint is present.')
    else:
        print("Constraint not found.")

    # Prints the corresponding values of Vitamin A constraint name
    print(test_constraints['Vitamin A'])

    # Changes the constraint key names and values and prints new values
    test_constraints['Vitamin A'] = {'minimum': '5', 'maximum:': '10'}
    print(test_constraints['Vitamin A'])

    # prints the number of constraints
    num_constraints = len(test_constraints)
    print("Number of constraints in test_constraints: ", num_constraints)

    # Deletes a constraint:
    del test_constraints['Vitamin A']
    num_constraints = len(test_constraints)
    print("Number of constraints after removing item :", num_constraints)

    # updates constraints value
    test_class.update_constraint('Vitamin A', 'min', 10)
    test_class.update_constraint('Vitamin A', 'max', 11)
    print(test_constraints['Vitamin A'])

    # Removes min constraint in Vitamin A
    test_class.remove_constraint('Vitamin A', 'min')
    print(test_constraints['Vitamin A'])

    # Prints the name of the optimizer class
    optimizer_name = test_class.get_name()
    print(optimizer_name)

    # Updates the name of the Optimizer class
    test_class.set_name("New Optimizer")
    optimizer_name = test_class.get_name()
    print(optimizer_name)

    # Returns constraints in a dictionary
    constraints_dict = test_class.get_constraints_dict()
    print(constraints_dict)

    # Update and Return new Constraints
    new_constraints = {'Vitamin D': {
        'min': 0, 'max': 10}, 'Vitamin E': {'min': 5}}
    test_class.set_constraints_dict(new_constraints)
    constraints_dict = test_class.get_constraints_dict()
    print(constraints_dict)

    # Reads the constraints dictionary associated with the key "test" and prints it
    test_class2 = OptimizerConstraints('New Constraints')
    test_class2.load_constraints_json('test_data_consts.json', 'test')
    constraints_dict = test_class2.get_constraints_dict()
    print(constraints_dict)

    # Dumps new constraints into json folder
    test_class2.dump_constraints_json('new_updated_constraints.json')


if __name__ == '__main__':
    test()
