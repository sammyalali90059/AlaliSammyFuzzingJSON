const fs = require('fs');
const path = require('path');
const JSON5 = require('json5');
const Bourne = require('@hapi/bourne');
const betterParse = require('json-parse-even-better-errors');
const safeParse = require('json-parse-safe');
const stringifySafe = require('json-stringify-safe');

const { performance } = require('perf_hooks');
const parsers = {
    "JSON.parse": JSON.parse,
    "fast-json-parse": data => require('fast-json-parse')(data).value,
    "JSON5.parse": require('json5').parse,
    "bourne": require('@hapi/bourne').parse,
    "better-parse": require('json-parse-even-better-errors'),
    "safe-stringify-parse": data => JSON.parse(require('json-stringify-safe')(data))
};

function testRandomAccess(parsedData) {
    // Randomly access elements within the parsed JSON data to simulate usage and check the presence of data.
    if (Array.isArray(parsedData) && parsedData.length > 0) {
        return parsedData[Math.floor(Math.random() * parsedData.length)] !== undefined ? "Yes" : "N/A";
    } else if (parsedData !== null && typeof parsedData === 'object' && Object.keys(parsedData).length > 0) {
        const keys = Object.keys(parsedData);
        return parsedData[keys[Math.floor(Math.random() * keys.length)]] !== undefined ? "Yes" : "N/A";
    }
    return "N/A";
}

function logResult(resultsFile, filePath, fileName, parserName, status, errorMessage = "", duration = 0, randomAccessResult = "N/A", memoryUsage = "N/A") {
    const row = `"${filePath}","${fileName}","${parserName}","${status}","${errorMessage.replace(/"/g, '""')}","${duration}","${randomAccessResult}","${memoryUsage}"\n`;
    // Logs results to a file including memory usage which shows how much memory was used after parsing.
    fs.appendFileSync(resultsFile, row);
}

function fuzzJsonWithParser(parserName, parserFunc, filePath, resultsFile) {
    const startTime = performance.now();
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        const parsedData = parserFunc(data);
        const randomAccessResult = testRandomAccess(parsedData);
        const duration = performance.now() - startTime;
        const memoryUsage = process.memoryUsage().heapUsed / 1024 / 1024; // Memory usage in MB
        // Log the successful parse operation, including duration and memory usage.
        logResult(resultsFile, filePath, path.basename(filePath), parserName, "Success", "", duration, randomAccessResult, memoryUsage.toFixed(2));
    } catch (e) {
        const duration = performance.now() - startTime;
        const memoryUsage = process.memoryUsage().heapUsed / 1024 / 1024; // Memory usage in MB
        // Log any errors encountered during parsing, including error message and memory usage.
        logResult(resultsFile, filePath, path.basename(filePath), parserName, "Error", e.message, duration, "N/A", memoryUsage.toFixed(2));
    }
}

function fuzzAllParsers(filePath, resultsFile) {
    Object.entries(parsers).forEach(([name, func]) => {
        fuzzJsonWithParser(name, func, filePath, resultsFile);
    });
}

function initializeResultsFile(resultsFile) {
    const headers = "File Path,File Name,Parser Name,Status,Error Message,Duration (ms),Random Access Result,Memory Usage (MB)\n";
    fs.writeFileSync(resultsFile, headers, 'utf8');
}

function fuzzDirectory(directoryPath) {
    const directoryName = path.basename(directoryPath);
    const resultsFile = path.join(directoryPath, `${directoryName}_results_JS.csv`);
    initializeResultsFile(resultsFile);
    fs.readdirSync(directoryPath).forEach(file => {
        if (file.endsWith('.json')) {
            const filePath = path.join(directoryPath, file);
            fuzzAllParsers(filePath, resultsFile);
        }
    });
    console.log(`Finished processing directory: ${directoryPath}`);
}

function main() {
    const baseDirectory = "C:/Users/Sammy/Documents/Thesis/AlaliSammyFuzzingJSON/JSONFiles";
    const directories = [
        path.join(baseDirectory, "real_json_files"),
        path.join(baseDirectory, "mutated_json_files"),
        path.join(baseDirectory, "1mbgenerated"),
        path.join(baseDirectory, "10mbgenerated"),
        path.join(baseDirectory, "100mbgenerated")
    ];
    directories.forEach(dir => fuzzDirectory(dir));
}

main();
