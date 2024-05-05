using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

class JsonFuzzer
{
    static Dictionary<string, Func<string, object>> parsers = new Dictionary<string, Func<string, object>>()
    {
        ["System.Text.Json"] = data => System.Text.Json.JsonSerializer.Deserialize<object>(data),
        ["Newtonsoft.Json"] = data => Newtonsoft.Json.JsonConvert.DeserializeObject<object>(data),
        ["Jil"] = data => Jil.JSON.Deserialize<object>(data),
        ["Utf8Json"] = data => Utf8Json.JsonSerializer.Deserialize<object>(data),
        ["ServiceStack.Text"] = data => ServiceStack.Text.JsonSerializer.DeserializeFromString<object>(data),
        ["FastJson"] = data => fastJSON.JSON.ToObject<object>(data)
    };

    static void Main(string[] args)
    {
        string baseDirectory = @"C:\Users\Sammy\Documents\Thesis\AlaliSammyFuzzingJSON\JSONFiles";
        var directories = new List<string>
        {
            Path.Combine(baseDirectory, "real_json_files"),
            Path.Combine(baseDirectory, "mutated_json_files"),
            Path.Combine(baseDirectory, "1mbgenerated"),
            Path.Combine(baseDirectory, "10mbgenerated"),
            Path.Combine(baseDirectory, "100mbgenerated")
        };

        foreach (var directory in directories)
        {
            FuzzDirectory(directory);
        }
    }

    static void FuzzDirectory(string directoryPath)
    {
        string directoryName = Path.GetFileName(directoryPath);
        string resultsFile = Path.Combine(directoryPath, $"{directoryName}_results.csv");

        InitializeResultsFile(resultsFile);

        foreach (var filePath in Directory.EnumerateFiles(directoryPath, "*.json"))
        {
            foreach (var parser in parsers)
            {
                FuzzJsonWithParser(parser.Key, parser.Value, filePath, resultsFile);
            }
        }
        Console.WriteLine($"Finished processing directory: {directoryPath}");
    }

    static void InitializeResultsFile(string resultsFile)
    {
        using (var writer = new StreamWriter(resultsFile, false))
        {
            writer.WriteLine("File Path,File Name,Parser Name,Status,Error Message,Duration (ms),Random Access Result,Memory Usage (MB)");
        }
    }

    static string TestRandomAccess(object jsonData)
    {
        // Randomly access elements in the parsed JSON data to simulate usage and verify integrity.
        if (jsonData is IDictionary<string, object> dict && dict.Count > 0)
        {
            var random = new Random();
            var randomKey = dict.Keys.ElementAt(random.Next(dict.Count));
            return dict[randomKey] != null ? "Yes" : "N/A";
        }
        else if (jsonData is List<object> list && list.Count > 0)
        {
            var random = new Random();
            var randomIndex = random.Next(list.Count);
            return list[randomIndex] != null ? "Yes" : "N/A";
        }
        return "N/A";
    }

    static void LogResult(string resultsFile, string filePath, string fileName, string parserName, string status, string errorMessage = "", long duration = 0, string randomAccessResult = "N/A")
    {
        // Escape quotes by doubling them
        string sanitizedErrorMessage = errorMessage.Replace("\"", "\"\"");
        using (var writer = new StreamWriter(resultsFile, true))
        {
            // Log the memory usage of the process after parsing the JSON file.
            writer.WriteLine($"\"{filePath}\",\"{fileName}\",\"{parserName}\",\"{status}\",\"{sanitizedErrorMessage}\",\"{duration}\",\"{randomAccessResult}\",\"{GC.GetTotalMemory(false) / (1024 * 1024)}\"");
        }
    }

    static void FuzzJsonWithParser(string parserName, Func<string, object> parserFunc, string filePath, string resultsFile)
    {
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();
        try
        {
            string data = File.ReadAllText(filePath);
            object parsedData = parserFunc(data);
            string randomAccessResult = TestRandomAccess(parsedData);
            stopwatch.Stop();
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Success", "", stopwatch.ElapsedMilliseconds, randomAccessResult);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Error", ex.Message, stopwatch.ElapsedMilliseconds);
        }
    }
}
