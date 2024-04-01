const fs = require('fs');
const path = require('path');
const fastJsonParse = require('fast-json-parse');
const JSON5 = require('json5');

const parsers = {
    "JSON.parse": JSON.parse,
    "fast-json-parse": data => fastJsonParse(data).value,
    "JSON5.parse": JSON5.parse
};

function initializeResultsFile() {
    const headers = ["File Path", "File Name", "Parser Name", "Status", "Error Message"];
    fs.writeFileSync('fuzzing_results_js.csv', headers.join(',') + '\n', 'utf8');
}

function logResult(filePath, fileName, parserName, status, errorMessage = "") {
    const row = [filePath, fileName, parserName, status, errorMessage].join(',');
    fs.appendFileSync('fuzzing_results_js.csv', row + '\n', 'utf8');
}

function fuzzJsonWithParser(parserName, parserFunc, filePath) {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        parserFunc(data);
        logResult(filePath, path.basename(filePath), parserName, "Success");
    } catch (e) {
        logResult(filePath, path.basename(filePath), parserName, "Error", e.message);
    }
}

function fuzzAllParsers(filePath) {
    Object.entries(parsers).forEach(([name, func]) => {
        fuzzJsonWithParser(name, func, filePath);
    });
}

function fuzzDirectory(directoryPath) {
    fs.readdirSync(directoryPath).forEach(file => {
        if (file.endsWith('.json')) {
            const filePath = path.join(directoryPath, file);
            fuzzAllParsers(filePath);
        }
    });
}

function main() {
    initializeResultsFile();
    const baseDirectory = "C:/Users/Sammy/Documents/Thesis";
    const directories = [
        path.join(baseDirectory, "real_json_files"),
        path.join(baseDirectory, "mutated_json_files"),
        path.join(baseDirectory, "generated_json_files_advanced")
    ];
    directories.forEach(dir => fuzzDirectory(dir));
}

main();
