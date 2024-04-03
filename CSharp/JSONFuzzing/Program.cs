using System;
using System.IO;
using System.Collections.Generic;
using System.Text.Json;
using Newtonsoft.Json;
using Jil;
using Utf8Json;
using RestSharp;
class JsonFuzzer
{
    static Dictionary<string, Action<string>> parsers = new Dictionary<string, Action<string>>()
    {
        ["System.Text.Json"] = data => System.Text.Json.JsonSerializer.Deserialize<object>(data),
        ["Newtonsoft.Json"] = data => Newtonsoft.Json.JsonConvert.DeserializeObject<object>(data),
        ["Jil"] = data => Jil.JSON.Deserialize<object>(data),
        ["Utf8Json"] = data => Utf8Json.JsonSerializer.Deserialize<object>(data),
        ["LitJson"] = data => LitJson.JsonMapper.ToObject(data),
        ["ServiceStack.Text"] = data => ServiceStack.Text.JsonSerializer.DeserializeFromString<object>(data),
        ["FastJson"] = data => fastJSON.JSON.ToObject(data)
    };

    static void Main(string[] args)
    {
        string baseDirectory = @"C:\Users\Sammy\Documents\Thesis\AlaliSammyFuzzingJSON\JSONFiles";
        string resultsDirectory = @"C:\Users\Sammy\Documents\Thesis\AlaliSammyFuzzingJSON\Results";
        string resultsFile = Path.Combine(resultsDirectory, "fuzzing_results_csharp.csv");

        InitializeResultsFile(resultsFile);
        var directories = new List<string>
        {
            //Path.Combine(baseDirectory, "generated_json_files_advanced"),
            Path.Combine(baseDirectory, "real_json_files")
            //Path.Combine(baseDirectory, "mutated_json_files")
        };

        foreach (var directory in directories)
        {
            FuzzDirectory(directory, resultsFile);
        }
    }

    static void InitializeResultsFile(string resultsFile)
    {
        using (var writer = new StreamWriter(resultsFile, false))
        {
            writer.WriteLine("File Path,File Name,Parser Name,Status,Error Message");
        }
    }

    static void LogResult(string resultsFile, string filePath, string fileName, string parserName, string status, string errorMessage = "")
    {
        using (var writer = new StreamWriter(resultsFile, true))
        {
            writer.WriteLine($"\"{filePath}\",\"{fileName}\",\"{parserName}\",\"{status}\",\"{errorMessage}\"");
        }
    }

    static void FuzzJsonWithParser(string parserName, Action<string> parserFunc, string filePath, string resultsFile)
    {
        try
        {
            string data = File.ReadAllText(filePath);
            parserFunc(data);
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Success");
        }
        catch (Exception ex)
        {
            LogResult(resultsFile, filePath, Path.GetFileName(filePath), parserName, "Error", ex.Message);
        }
    }

    static void FuzzDirectory(string directoryPath, string resultsFile)
    {
        foreach (var filePath in Directory.EnumerateFiles(directoryPath, "*.json"))
        {
            foreach (var parser in parsers)
            {
                FuzzJsonWithParser(parser.Key, parser.Value, filePath, resultsFile);
            }
        }
        Console.WriteLine($"Finished processing directory: {directoryPath}");
    }
}
