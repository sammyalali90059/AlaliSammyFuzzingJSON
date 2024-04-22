import os
import csv
import json
import ujson
import simplejson
import orjson
import json5
import rapidjson
import ijson
from pyjson5 import loads as json5py_loads
import json_parser
import multiprocessing
from multiprocessing import Pool

# Mapping parser functions for convenience
def ijson_parse(data):
    return next(ijson.items(data, ''))

# Update the parser dictionary
parsers = {
    "json": json.loads,
    "ujson": ujson.loads,
    "simplejson": simplejson.loads,
    "orjson": orjson.loads,
    "json5": json5.loads,
    "rapidjson": rapidjson.loads,
    "ijson": ijson_parse,  # Use the new regular function
    "pyjson5": json5py_loads,
    "json_parser": json_parser.parse
}

def initialize_results_file(results_file):
    """Initializes the fuzzing results CSV file with headers."""
    with open(results_file, 'w', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow(["File Path", "File Name", "Parser Name", "Status", "Error Message"])

def log_result(results_file, file_path, file_name, parser_name, status, error_message=""):
    """Logs the result of a parsing attempt to a CSV file."""
    with open(results_file, 'a', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow([file_path, file_name, parser_name, status, error_message])

def fuzz_json_with_parser(parser_name, parser_func, file_path, results_file):
    """Wrapper for parsing and logging."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            parsed_data = parser_func(data)
            if isinstance(parsed_data, dict) and parsed_data:
                first_key = next(iter(parsed_data))
                _ = parsed_data[first_key]
            elif isinstance(parsed_data, list) and parsed_data:
                _ = parsed_data[0]
        file_name = os.path.basename(file_path)
        log_result(results_file, file_path, file_name, parser_name, "Success")
    except Exception as e:
        file_name = os.path.basename(file_path)
        log_result(results_file, file_path, file_name, parser_name, "Error", str(e))

def main():
    base_directory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/JSONFiles"
    results_directory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/Results"
    results_file = os.path.join(results_directory, "fuzzing_results_python.csv")
    initialize_results_file(results_file)

    # Get all JSON file paths
    json_files = []
    directories = [os.path.join(base_directory, "real_json_files")]
    for directory in directories:
        json_files.extend([os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith(".json")])
    
    # Prepare arguments for parallel processing
    args = [(parser_name, parser_func, file_path, results_file) for file_path in json_files for parser_name, parser_func in parsers.items()]

    # Use a single pool to handle all parsing tasks
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.starmap(fuzz_json_with_parser, args)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
