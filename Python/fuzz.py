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

# Mapping parser functions for convenience
parsers = {
    "json": json.loads,
    "ujson": ujson.loads,
    "simplejson": simplejson.loads,
    "orjson": orjson.loads,
    "json5": json5.loads,
    "rapidjson": rapidjson.loads,
    "ijson": lambda data: next(ijson.items(data, '')),
    "pyjson5": json5py_loads
}

def initialize_results_file():
    """Initializes the fuzzing results CSV file with headers."""
    with open('fuzzing_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow(["File Path", "File Name", "Parser Name", "Status", "Error Message"])

def log_result(file_path, file_name, parser_name, status, error_message=""):
    """Logs the result of a parsing attempt to a CSV file."""
    with open('fuzzing_results.csv', 'a', newline='', encoding='utf-8') as csvfile:
        result_writer = csv.writer(csvfile)
        result_writer.writerow([file_path, file_name, parser_name, status, error_message])

def fuzz_json_with_parser(parser_name, parser_func, file_path):
    """Attempts to parse a JSON file with the specified parser and logs the outcome."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            parser_func(data)
        # Extract file name from file path
        file_name = os.path.basename(file_path)
        log_result(file_path, file_name, parser_name, "Success")
    except Exception as e:
        file_name = os.path.basename(file_path)  # Extract file name here as well for consistency
        log_result(file_path, file_name, parser_name, "Error", str(e))

def fuzz_all_parsers(file_path):
    """Attempts to parse a JSON file with all specified parsers."""
    for parser_name, parser_func in parsers.items():
        fuzz_json_with_parser(parser_name, parser_func, file_path)

def fuzz_directory(directory_path):
    """Fuzzes all JSON files within a given directory."""
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            fuzz_all_parsers(file_path)

def main():
    initialize_results_file()
    base_directory = "C:/Users/Sammy/Documents/Thesis"  # Adjust this path to your actual base directory
    directories = [
        os.path.join(base_directory, "real_json_files"),
        os.path.join(base_directory, "mutated_json_files"),
        os.path.join(base_directory, "generated_json_files_advanced")
    ]
    for directory in directories:
        fuzz_directory(directory)


if __name__ == "__main__":
    main()
