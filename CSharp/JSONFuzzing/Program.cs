using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics; // Import for timing

class JsonFuzzer
{
    static Dictionary<string, Action<string>> parsers = new Dictionary<string, Action<string>>()
    {
        ["System.Text.Json"] = data => DeserializeAndTest(System.Text.Json.JsonSerializer.Deserialize<object>(data)),
        ["Newtonsoft.Json"] = data => DeserializeAndTest(Newtonsoft.Json.JsonConvert.DeserializeObject<object>(data)),
        ["Jil"] = data => DeserializeAndTest(Jil.JSON.Deserialize<object>(data)),
        ["Utf8Json"] = data => DeserializeAndTest(Utf8Json.JsonSerializer.Deserialize<object>(data)),
        ["ServiceStack.Text"] = data => DeserializeAndTest(ServiceStack.Text.JsonSerializer.DeserializeFromString<object>(data)),
        ["FastJson"] = data => DeserializeAndTest(fastJSON.JSON.ToObject<object>(data))
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
            writer.WriteLine("File Path,File Name,Parser Name,Status,Error Message,Duration (ms)");
        }
    }

    static void LogResult(string resultsFile, string filePath, string fileName, string parserName, string status, string errorMessage = "", long duration = 0)
    {
        // Escape quotes by doubling them
        string sanitizedErrorMessage = errorMessage.Replace("\"", "\"\"");

        using (var writer = new StreamWriter(resultsFile, true))
        {
            writer.WriteLine($"\"{filePath}\",\"{fileName}\",\"{parserName}\",\"{status}\",\"{sanitizedErrorMessage}\",\"{duration}\"");
        }
    }

    static void FuzzJsonWithParser(string parserName, Action<string> parserFunc, string filePath, string resultsFile)
    {
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();
        try
        {
            string data = File.ReadAllText(filePath);
            parserFunc(data);
            stopwatch.Stop();
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Success", duration: stopwatch.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Error", ex.Message, stopwatch.ElapsedMilliseconds);
        }
    }

    static void DeserializeAndTest(object jsonData)
    {
        if (jsonData is IDictionary<string, object> dict && dict.Count > 0)
        {
            var firstKey = dict.Keys.GetEnumerator();
            firstKey.MoveNext();
            _ = dict[firstKey.Current];
        }
        else if (jsonData is List<object> list && list.Count > 0)
        {
            _ = list[0];
        }
    }
}
