import json
import random
import os

def create_random_json(depth=0, MAX_DEPTH=10, CHANCE_TO_NEST=0.8):
    DATA_TYPES = ["string", "number", "object", "array", "boolean", "null", "email", "url"]

    def random_string(length=None):
        if length is None:
            length = random.randint(5, 20)
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ') for _ in range(length))

    def random_email():
        return f"{random_string(5)}@{random_string(5)}.com"

    def random_url():
        return f"http://www.{random_string(5)}.com/{random_string(5)}"

    def random_value(data_type):
        if data_type == "string":
            return random_string() + random.choice(['\n', '\t', '\\', '"', ''])  # Special characters
        elif data_type == "number":
            return random.randint(-10000, 10000)
        elif data_type == "object":
            return create_random_json(depth + 1)
        elif data_type == "array":
            return [random_value(random.choice(DATA_TYPES[:-3])) for _ in range(random.randint(1, 5))]
        elif data_type == "boolean":
            return random.choice([True, False])
        elif data_type == "null":
            return None
        elif data_type == "email":
            return random_email()
        elif data_type == "url":
            return random_url()

    if depth >= MAX_DEPTH:
        return {"key": random_value(random.choice(DATA_TYPES[:-2]))}  # Exclude email and url for base case

    json_object = {}
    num_keys = random.randint(1, 5)
    for _ in range(num_keys):
        key = random_string(random.randint(3, 10))  # Keys with special characters
        data_type = random.choice(DATA_TYPES)
        json_object[key] = random_value(data_type)

    # Introduce an array of objects or objects within arrays randomly
    if random.random() < CHANCE_TO_NEST and depth < MAX_DEPTH - 1:
        if random.choice([True, False]):
            json_object[random_string(5)] = [create_random_json(depth + 2) for _ in range(random.randint(2, 4))]
        else:
            json_object[random_string(5)] = {random_string(5): [random_value(random.choice(DATA_TYPES[:-3])) for _ in range(random.randint(2, 4))]}

    return json_object

def generate_json_files(num_files, directory, file_prefix="grammar"):
    os.makedirs(directory, exist_ok=True)
    for i in range(num_files):
        json_obj = create_random_json()
        file_path = os.path.join(directory, f"{file_prefix}_{i+1}.json")
        with open(file_path, 'w') as f:
            json.dump(json_obj, f, indent=2)

output_directory = "C:/Users/Sammy/Documents/Thesis/json_grammars"  # Change this to your preferred directory
generate_json_files(2500, output_directory, "enhanced_grammar")
print(f"2500 enhanced JSON grammar files have been generated in {output_directory}.")
