const fs = require('fs');
const path = require('path');
const fastJsonParse = require('fast-json-parse');
const JSON5 = require('json5');
const Bourne = require('@hapi/bourne');
const { parse: flattedParse } = require('flatted');
const betterParse = require('json-parse-even-better-errors');
const { parse: safeParse } = require('json-parse-safe');
const stringifySafe = require('json-stringify-safe');

const parsers = {
    "JSON.parse": JSON.parse,
    "fast-json-parse": data => fastJsonParse(data).value,
    "JSON5.parse": JSON5.parse,
    "bourne": data => Bourne.parse(data),
    "better-parse": betterParse,
    "safe-stringify-parse": data => JSON.parse(stringifySafe(data)),
    "flatted-parse": flattedParse,
    "safe-parse": data => {
        const result = safeParse(data);
        if (result.error) {
            throw new Error(result.error); // This will handle the case where there is an error in parsing
        }
        return result.value; // Return the parsed data
    }
};

function initializeResultsFile(resultsFile) {
    const headers = ["File Path", "File Name", "Parser Name", "Status", "Error Message"];
    fs.writeFileSync(resultsFile, headers.join(',') + '\n', 'utf8');
}

function logResult(resultsFile, filePath, fileName, parserName, status, errorMessage = "") {
    const row = [`"${filePath}"`, `"${fileName}"`, `"${parserName}"`, `"${status}"`, `"${errorMessage.replace(/"/g, '""')}"`].join(',');
    fs.appendFileSync(resultsFile, row + '\n', 'utf8');
}

function fuzzJsonWithParser(parserName, parserFunc, filePath, resultsFile) {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        const parsedData = parserFunc(data);
        // Access the first element or a specific key if the parser returns an object
        if (typeof parsedData === 'object' && parsedData !== null) {
            const firstKey = Object.keys(parsedData)[0];
            const value = parsedData[firstKey]; // Accessing the value of the first key
        }
        logResult(resultsFile, filePath, path.basename(filePath), parserName, "Success");
    } catch (e) {
        logResult(resultsFile, filePath, path.basename(filePath), parserName, "Error", e.message);
    }
}

function fuzzAllParsers(filePath, resultsFile) {
    Object.entries(parsers).forEach(([name, func]) => {
        fuzzJsonWithParser(name, func, filePath, resultsFile);
    });
}

function fuzzDirectory(directoryPath, resultsFile) {
    fs.readdirSync(directoryPath).forEach(file => {
        if (file.endsWith('.json')) {
            const filePath = path.join(directoryPath, file);
            fuzzAllParsers(filePath, resultsFile);
        }
    });
}

function main() {
    const baseDirectory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/JSONFiles";
    const resultsDirectory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/Results";
    const resultsFile = path.join(resultsDirectory, "fuzzing_results_js.csv");
    initializeResultsFile(resultsFile);
    const directories = [
        path.join(baseDirectory, "real_json_files"),
        path.join(baseDirectory, "mutated_json_files"),
        path.join(baseDirectory, "generated_json_files_advanced")
    ];
    directories.forEach(dir => fuzzDirectory(dir, resultsFile));
}

main();
