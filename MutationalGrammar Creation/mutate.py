import json
import random
import copy
import os
from pathlib import Path

# Define paths to the directories
real_files_dir = Path("real_json_files")
mutated_files_dir = Path("mutated_json_files")

os.makedirs(mutated_files_dir, exist_ok=True)

def shuffle_dict(d):
    """Returns a new dictionary with keys shuffled."""
    keys = list(d.keys())
    random.shuffle(keys)
    return {key: d[key] for key in keys}

def mutate_json(original_json):
    mutated_json = copy.deepcopy(original_json)
    
    def mutate_structure(value):
        """Mutates the JSON structure, altering the ordering, nesting, and type changes."""
        if isinstance(value, dict):
            #shuffling dictionary
            #for example
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #Shuffled dictionary: {'b': 2, 'c': 3, 'a': 1}
            value = shuffle_dict(value)
            
            #Randomly nest the dictionary
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #After nesting: {'a': 1, 'b': 2, 'c': {'nested_key': 3}}
            if random.choice([True, False]):
                key = random.choice(list(value.keys()))
                value[key] = {'nested_key': value[key]}
                
            #Remove a random key
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #After removing a key: {'a': 1, 'c': 3}
            if random.choice([True, False]) and value:
                key_to_remove = random.choice(list(value.keys()))
                value.pop(key_to_remove)
                
            # Duplicate a key with altered value
            
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #After duplicating key 'b': {'a': 1, 'b': 2, 'b_dup': 2}
            if value:
                key_to_duplicate = random.choice(list(value.keys()))
                value[key_to_duplicate + '_dup'] = mutate_value(value[key_to_duplicate])
            
            #Introduce deeper nesting for objects
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #After deeper nesting: {'nested_deep': {'a': 1, 'b': 2, 'c': 3}}
            if random.choice([True, False]):
                value = {'nested_deep': value}
            
            #Introduce new random key-value pairs
            #Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            #After introducing new pair: {'a': 1, 'b': 2, 'c': 3, 'random_key_55': -42}

            if random.choice([True, False]):
                random_key = f'random_key_{random.randint(1, 100)}'
                value[random_key] = random.randint(-100, 100)

        elif isinstance(value, list):
            #Shuffle list order
            #Input list: [1, 2, 3, 4, 5]
            #Shuffled list: [5, 1, 4, 2, 3]

            random.shuffle(value)
            
            # Remove a random item
            #Input list: [1, 2, 3, 4, 5]
            #After removing a random item: [1, 2, 3, 5]
            if len(value) > 1 and random.choice([True, False]):
                value.pop(random.randrange(len(value)))

            #Nest a list within the list
            #Input list: [1, 2, 3, 4, 5]
            #After nesting: [1, [2, {'nested': 'object'}], 3, 4, 5]  
            if random.choice([True, False]):
                index = random.randrange(len(value))
                value[index] = [value[index], {'nested': 'object'}]
                
            #Duplicate a list item
            #Input list: [1, 2, 3, 4, 5]
            #After duplicating an item: [1, 2, 3, 4, 5, 3]
            if value:
                item_to_duplicate = random.choice(value)
                value.append(item_to_duplicate)
            
            #Combine two arrays into one or split an array into two
            if len(value) > 2 and random.choice([True, False]):
                midpoint = len(value) // 2
                if random.choice([True, False]):
                    #Combine
                    value = value[:midpoint] + value[midpoint:]
                else:
                    #Split
                    value = [value[:midpoint], value[midpoint:]]

        return value

    def mutate_value(value):
        """Mutates the value based on its type with additional structural changes."""
        if isinstance(value, (dict, list)):
            return mutate_structure(value)
        elif isinstance(value, str):
            if value.isdigit():  #Convert string numbers to integers
                return int(value)
            elif value.lower() == 'true':  # Convert 'true' to boolean True
                return True
            elif value.lower() == 'false':  # Convert 'false' to boolean False
                return False
            else:
                return random.choice([value.upper(), value.lower(), value + "_mutated"])
        elif isinstance(value, bool):
            return not value
        elif isinstance(value, int):
            return value + random.randint(-10, 10)
        elif isinstance(value, float):
            return value * random.uniform(0.8, 1.2)
        elif isinstance(value, (int, float)) and random.choice([True, False]):
            return str(value)  # Convert a number to a string representation
        else:
            return value  # Return as is if the type is not handled

    return mutate_value(mutated_json)

# File processing loop with error handling
for file_path in real_files_dir.glob("*.json"):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        mutated_data = mutate_json(data)
        
        new_file_name = f"{file_path.stem}_mutated{file_path.suffix}"
        new_file_path = mutated_files_dir / new_file_name
        
        with open(new_file_path, 'w') as file:
            json.dump(mutated_data, file, indent=4)
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
