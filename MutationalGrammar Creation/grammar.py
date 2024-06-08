import os
import random
import ujson as json  # Using ujson for faster serialization
from multiprocessing import Pool, cpu_count

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
            return random_string() + random.choice(['\n', '\t', '\\', '"', ''])
        elif data_type == "number":
            return random.randint(-10000, 10000)
        elif data_type == "object":
            return create_random_json(depth + 1, MAX_DEPTH, CHANCE_TO_NEST)
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
        return {"key": random_value(random.choice(DATA_TYPES[:-2]))}
    
    json_object = {}
    num_keys = random.randint(1, 5)
    for _ in range(num_keys):
        key = random_string(random.randint(3, 10))
        data_type = random.choice(DATA_TYPES)
        json_object[key] = random_value(data_type)
    
    if random.random() < CHANCE_TO_NEST and depth < MAX_DEPTH - 1:
        if random.choice([True, False]):
            json_object[random_string(5)] = [create_random_json(depth + 2, MAX_DEPTH, CHANCE_TO_NEST) for _ in range(random.randint(2, 4))]
        else:
            json_object[random_string(5)] = {random_string(5): [random_value(random.choice(DATA_TYPES[:-3])) for _ in range(random.randint(2, 4))]}
    
    return json_object

def generate_and_write_json_file(args):
    size, index, current_directory, file_prefix = args
    target_size = size * 1024 * 1024  # Target size in bytes
    json_array = []
    while sum(len(json.dumps(item).encode('utf-8')) for item in json_array) < target_size:
        json_obj = create_random_json()
        json_array.append(json_obj)
    final_json_string = json.dumps(json_array, indent=2)
    file_path = os.path.join(current_directory, f"{file_prefix}_{index+1}.json")
    with open(file_path, 'w') as f:
        f.write(final_json_string)

def generate_json_files(num_files, directory, file_sizes, file_prefix="grammar"):
    os.makedirs(directory, exist_ok=True)
    process_args = []
    for size in file_sizes:
        current_directory = os.path.join(directory, f"{size}MB")
        os.makedirs(current_directory, exist_ok=True)
        for i in range(num_files // len(file_sizes)):
            process_args.append((size, i, current_directory, file_prefix))
    
    with Pool(cpu_count()) as pool:
        pool.map(generate_and_write_json_file, process_args)

if __name__ == '__main__':
    output_directory = "C:/Users/Sammy/Documents/Thesis/json_grammars_new_finall"  
    file_sizes = [1,10,100]  
    generate_json_files(2500, output_directory, file_sizes)
    print(f"JSON grammar files of varying sizes have been generated in {output_directory}.")
