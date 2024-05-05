import os
import csv
import time
import json
import ujson
import simplejson
import orjson
import json5
import rapidjson
import ijson
from pyjson5 import loads as json5py_loads
import json_parser
import random
import psutil
import concurrent.futures

# Define a dictionary with various JSON parsing libraries.
parsers = {
    "json": json.loads,
    "ujson": ujson.loads,
    "simplejson": simplejson.loads,
    "orjson": orjson.loads,
    "json5": json5.loads,
    "rapidjson": rapidjson.loads,
    "ijson": lambda data: next(ijson.items(data, '')),
    "pyjson5": json5py_loads,
    "json_parser": json_parser.parse
}

def initialize_results_file(results_file):
    # Create and initialize the CSV results file with appropriate headers.
    with open(results_file, 'w', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow(["File Path", "File Name", "Parser Name", "Status", "Error Message", "Duration (ms)", "Random Access Result", "Memory Usage (MB)"])

def log_result(results_file, file_path, file_name, parser_name, status, error_message="", duration=0, random_access_result="N/A", memory_usage="N/A"):
    # Log each result into the CSV file including memory usage and random access result.
    with open(results_file, 'a', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow([file_path, file_name, parser_name, status, error_message, duration, random_access_result, memory_usage])

def test_random_access(parsed_data):
    # Perform a random access test on parsed data to validate JSON integrity and presence of data.
    if isinstance(parsed_data, dict) and parsed_data:
        random_key = random.choice(list(parsed_data.keys()))
        return "Yes" if parsed_data.get(random_key) else "N/A"
    elif isinstance(parsed_data, list) and parsed_data:
        random_index = random.randint(0, len(parsed_data) - 1)
        return "Yes" if parsed_data[random_index] else "N/A"
    return "N/A"

def fuzz_json_with_parser(parser_name, parser_func, data, file_path, results_file):
    start_time = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Using a thread pool to parallelize parsing with a timeout of 60 seconds.
            future = executor.submit(parser_func, data)
            parsed_data = future.result(timeout=60)  # Timeout set to 60 seconds
        random_access_result = "N/A"
        if isinstance(parsed_data, (dict, list)):
            random_access_result = test_random_access(parsed_data)
        duration = round((time.time() - start_time) * 1000, 2)  # Calculate the duration in milliseconds.
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Memory usage in MB.
        log_result(results_file, file_path, os.path.basename(file_path), parser_name, "Success", "", duration, random_access_result, memory_usage)
    except concurrent.futures.TimeoutError:
        duration = round((time.time() - start_time) * 1000, 2)
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        log_result(results_file, file_path, os.path.basename(file_path), parser_name, "Error", "Timeout", duration, "N/A", memory_usage)
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        log_result(results_file, file_path, os.path.basename(file_path), parser_name, "Error", str(e), duration, "N/A", memory_usage)

def fuzz_directory(directory_path):
    # Process each JSON file in the specified directory using all available parsers.
    directory_name = os.path.basename(directory_path)
    results_file = os.path.join(directory_path, f"{directory_name}_results_python.csv")
    initialize_results_file(results_file)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read()
                    for parser_name, parser_func in parsers.items():
                        futures.append(
                            executor.submit(fuzz_json_with_parser, parser_name, parser_func, data, file_path, results_file)
                        )
        for future in concurrent.futures.as_completed(futures):
            pass  # Handle results or exceptions as needed.

    print(f"Finished processing directory: {directory_path}")

def main():
    # Main function to start the fuzzing process for all JSON files in multiple directories.
    base_directory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/JSONFiles"
    directories = [
        os.path.join(base_directory, "real_json_files"),
        os.path.join(base_directory, "mutated_json_files"),
        os.path.join(base_directory, "1mbgenerated"),
        os.path.join(base_directory, "10mbgenerated"),
        os.path.join(base_directory, "100mbgenerated")
    ]
    for directory in directories:
        fuzz_directory(directory)

if __name__ == "__main__":
    main()
