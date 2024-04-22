import json
import random
import copy
import os
from pathlib import Path

#add invalid json, try to break more, open quotes dont close, open one close two etc
#try to make some files bigger
#breakage files
#scale with size of file

#Broken samples in mutational
#aim to 100mb files, 1,10,100
# Define directory paths

real_files_dir = Path(r"C:\Users\Sammy\Documents\Thesis\AlaliSammyFuzzingJSON\JSONFiles\real_json_files")
mutated_files_dir = Path("mutated_json_files")

os.makedirs(mutated_files_dir, exist_ok=True)

def shuffle_dict(d):
    keys = list(d.keys())
    random.shuffle(keys)
    return {key: d[key] for key in keys}
    
def break_json(json_str): #Write where you got this
    breaks = [
        lambda s: s[:-1],  # Remove the last character.
        lambda s: s.replace(':', ',', 1),  # Replace first colon with a comma.
        lambda s: s.replace('{', '[', 1),  # Replace an opening brace with a bracket.
        lambda s: s[:-1] + ',',  # Add a comma after the last character.
        lambda s: '{"broken": ' + s + '}',  # Incorrect nesting.
        lambda s: s.replace('"', '\'', 1),  # Replace first double quote with a single.
        lambda s: s + ',"extra":undefined',  # Append invalid element.
        lambda s: '{' + s[1:],  # Remove first character, add brace.
        lambda s: s + (']' if s.strip().endswith('}') else '}'),  # Wrong bracket/brace.
        lambda s: json.dumps(json.loads(s), ensure_ascii=False).replace(":", "\t"),  # Use tab instead of colon.
        lambda s: s.replace("true", "ture"),  # Misspell true.
        lambda s: s[:10] + '"' + s[10:],  # Random insertion of quote.
        lambda s: s.replace('}', '}{' * 10),  # Excessive braces.
        lambda s: "{" + ", ".join(s.strip('{}').split(',')) + "}",  # Flatten structure.
        lambda s: s + ',"extra":' + '{"nested":' * 10 + 'false' + '}' * 10,  # Deep nesting.
        lambda s: s + '"',  # Open quote but don't close.
        lambda s: s[:-1] + '"' if s.endswith('"') else s + '"',  # Close open quote if it's open, otherwise open a new one.
        lambda s: s + '}}' if s.count('{') > s.count('}') else s + '{{',  # Unbalance braces to open more than close or vice versa.
        lambda s: s + ']]' if s.count('[') > s.count(']') else s + '[['  # Unbalance brackets to open more than close or vice versa.
    ]
    random.shuffle(breaks)  # Shuffle the list of mutation functions.
    return random.choice(breaks)(json_str)  # Apply one randomly chosen mutation.

def mutate_json(original_json):
    mutated_json = copy.deepcopy(original_json)
    intentionally_broken = False  # Flag to indicate intentional breaking

    def mutate_structure(value):
        nonlocal intentionally_broken
        if isinstance(value, dict):
            # Shuffling dictionary
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # Shuffled dictionary: {'b': 2, 'c': 3, 'a': 1}
            value = shuffle_dict(value)
            
            # Randomly nest the dictionary
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # After nesting: {'a': 1, 'b': 2, 'c': {'nested_key': 3}}
            if random.choice([True, False]):
                key = random.choice(list(value.keys()))
                value[key] = {'nested_key': value[key]}
                
                               
            # Remove a random key
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # After removing a key: {'a': 1, 'c': 3}
            if random.choice([True, False]) and value:
                key_to_remove = random.choice(list(value.keys()))
                value.pop(key_to_remove)
                
                
            # Duplicate a key with altered value
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # After duplicating key 'b': {'a': 1, 'b': 2, 'b_dup': 2}
            if value:
                key_to_duplicate = random.choice(list(value.keys()))
                value[key_to_duplicate + '_dup'] = mutate_value(value[key_to_duplicate])
                
            
            # Introduce deeper nesting for objects
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # After deeper nesting: {'nested_deep': {'a': 1, 'b': 2, 'c': 3}}
            if random.choice([True, False]):
                value = {'nested_deep': value}
                
            # Introduce new random key-value pairs
            # For example
            # Input dictionary: {'a': 1, 'b': 2, 'c': 3}
            # After introducing new pair: {'a': 1, 'b': 2, 'c': 3, 'random_key_55': -42}   
            if random.choice([True, False]):
                random_key = f'random_key_{random.randint(1, 100)}'
                value[random_key] = random.randint(-100, 100)
        elif isinstance(value, list):
            # Shuffle list order
            # For example
            # Input list: [1, 2, 3, 4, 5]
            # Shuffled list: [5, 1, 4, 2, 3]
            random.shuffle(value)
            
            # Remove a random item
            # For example
            # Input list: [1, 2, 3, 4, 5]
            # After removing a random item: [1, 2, 3, 5]
            if len(value) > 1 and random.choice([True, False]):
                value.pop(random.randrange(len(value)))
                
            # Nest a list within the list
            # For example
            # Input list: [1, 2, 3, 4, 5]
            # After nesting: [1, [2, {'nested': 'object'}], 3, 4, 5]  
            if random.choice([True, False]):
                index = random.randrange(len(value))
                value[index] = [value[index], {'nested': 'object'}]
                
            # Duplicate a list item
            # For example
            # Input list: [1, 2, 3, 4, 5]
            # After duplicating an item: [1, 2, 3, 4, 5, 3]
            if value:
                item_to_duplicate = random.choice(value)
                value.append(item_to_duplicate)
                
            # Combine two arrays into one or split an array into two
            # Example of combining
            if len(value) > 2 and random.choice([True, False]):
                midpoint = len(value) // 2
                value = [value[:midpoint], value[midpoint:]]

        # Always break the JSON
        intentionally_broken = True
        return break_json(json.dumps(value, ensure_ascii=False)), True

    def mutate_value(value):
        if isinstance(value, (dict, list)):
            return mutate_structure(value)
        elif isinstance(value, str):
            if value.isdigit():
                return int(value), False
            elif value.lower() == 'true':
                return True, False
            elif value.lower() == 'false':
                return False, False
            return random.choice([value.upper(), value.lower(), value + "_mutated"]), False
        elif isinstance(value, bool):
            return not value, False
        elif isinstance(value, int):
            return value + random.randint(-10, 10), False
        elif isinstance(value, float):
            return value * random.uniform(0.8, 1.2), False
        return value, False  # Return as is if the type is not handled

    mutated_data, intentionally_broken = mutate_value(mutated_json)
    return mutated_data, intentionally_broken

# File processing loop with error handling
for file_path in real_files_dir.glob("*.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        mutated_data, was_intentionally_broken = mutate_json(data)
    except json.JSONDecodeError as decode_err:
        print(f"JSONDecodeError for {file_path}: {decode_err}. Reading raw content.")
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            mutated_data = file.read()
        was_intentionally_broken = True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        continue

    new_file_name = f"{file_path.stem}_mutated{('_intentionallyBroken' if was_intentionally_broken else '')}{file_path.suffix}"
    new_file_path = mutated_files_dir / new_file_name
    with open(new_file_path, 'w', encoding='utf-8', errors='replace') as file:
        if isinstance(mutated_data, dict):
            mutated_data = json.dumps(mutated_data, ensure_ascii=False)  # Convert dict to string
        elif not isinstance(mutated_data, str):
            mutated_data = str(mutated_data)  # Convert non-string data to string
        file.write(mutated_data)  # Write as raw string
