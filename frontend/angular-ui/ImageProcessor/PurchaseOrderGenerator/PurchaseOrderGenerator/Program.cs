using System.Text;
using System.Text.Json;

namespace PurchaseOrderGenerator;

class Program
{
    private static readonly HttpClient httpClient = new HttpClient
    {
        Timeout = TimeSpan.FromMinutes(5) // Increase timeout to 5 minutes for vision model processing
    };
    private const string OllamaApiUrl = "http://localhost:11434/api/chat";
    private const string DefaultModel = "llava"; // Vision model for object detection

    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Purchase Order Reader using Ollama ===\n");

        // Get the Image folder path (at the root level, same as PurchaseOrderGenerator folder)
        // Try multiple possible locations based on where the application is run from
        string imageFolder = "";
        
        // Get the base directory of the executable or current directory
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string currentDir = Directory.GetCurrentDirectory();
        
        // Try from executable location (if running from bin folder)
        string parentFromBin = Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "Image"));
        if (Directory.Exists(parentFromBin))
        {
            imageFolder = parentFromBin;
        }
        // Try relative path from current directory (if running from project root)
        else if (Directory.Exists(Path.Combine(currentDir, "..", "Image")))
        {
            imageFolder = Path.GetFullPath(Path.Combine(currentDir, "..", "Image"));
        }
        // Try absolute path from parent directory
        else
        {
            string parentDir = Directory.GetParent(currentDir)?.FullName ?? currentDir;
            imageFolder = Path.Combine(parentDir, "Image");
        }

        // Validate Image folder exists
        if (!Directory.Exists(imageFolder))
        {
            Console.WriteLine($"Error: Image folder not found: {imageFolder}");
            Console.WriteLine("Please ensure the Image folder exists in the project directory.");
            return;
        }

        Console.WriteLine($"Image folder: {imageFolder}\n");

        // Check if Ollama is running
        if (!await CheckOllamaRunningAsync())
        {
            Console.WriteLine("Error: Ollama is not running or not accessible.");
            Console.WriteLine("Please start Ollama by running: ollama serve");
            Console.WriteLine("Or make sure Ollama service is running.");
            return;
        }

        // Get all image files from the Image folder
        string[] imageExtensions = { "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif" };
        var imageFiles = new List<string>();
        foreach (var extension in imageExtensions)
        {
            imageFiles.AddRange(Directory.GetFiles(imageFolder, extension, SearchOption.TopDirectoryOnly));
        }

        if (imageFiles.Count == 0)
        {
            Console.WriteLine("No image files found in the Image folder.");
            return;
        }

        Console.WriteLine($"Found {imageFiles.Count} image file(s) to process.\n");

        // Process each image one by one
        int processedCount = 0;
        foreach (string imagePath in imageFiles)
        {
            try
            {
                processedCount++;
                string fileName = Path.GetFileName(imagePath);
                Console.WriteLine($"\n[{processedCount}/{imageFiles.Count}] Processing: {fileName}");

                // Convert image to base64
                byte[] imageBytes = await File.ReadAllBytesAsync(imagePath);
                string base64Image = Convert.ToBase64String(imageBytes);
                Console.WriteLine($"Image encoded ({imageBytes.Length / 1024} KB)");

                // Read purchase order from image
                string result = await ReadPurchaseOrderAsync(base64Image, imagePath);

                // Print the result
                Console.WriteLine($"\n=== Purchase Order Data ===\n{result.Trim()}\n");

                // Delete the image file
                File.Delete(imagePath);
                Console.WriteLine($"✓ Image deleted: {fileName}");
            }
            catch (TaskCanceledException ex)
            {
                Console.WriteLine($"\n✗ Error: Request timed out for {Path.GetFileName(imagePath)}");
                Console.WriteLine($"Details: {ex.Message}");
                // Continue with next image
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"\n✗ Error: Could not connect to Ollama API for {Path.GetFileName(imagePath)}");
                Console.WriteLine($"Details: {ex.Message}");
                // Continue with next image
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n✗ Error processing {Path.GetFileName(imagePath)}: {ex.Message}");
                // Continue with next image
            }
        }

        Console.WriteLine($"\n=== Processing Complete ===");
        Console.WriteLine($"Processed {processedCount} image(s) from {imageFiles.Count} total file(s).");
    }

    static async Task<bool> CheckOllamaRunningAsync()
    {
        try
        {
            using var testClient = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            var response = await testClient.GetAsync("http://localhost:11434/api/tags");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    static async Task<string> ReadPurchaseOrderAsync(string base64Image, string imagePath)
    {
        // Create the request payload for Ollama API
        var requestPayload = new
        {
            model = DefaultModel,
            messages = new[]
            {
                new
                {
                    role = "user",
                    content = "You are an OCR system for reading purchase orders. Read and extract all information from this purchase order image. Extract details such as: order number, date, vendor/supplier name, items with descriptions, quantities, prices, totals, shipping address, billing address, and any other relevant information. Present the information in a clear, structured format with labeled fields.",
                    images = new[] { base64Image }
                }
            },
            stream = false,
            options = new
            {
                temperature = 0.0
            }
        };

        string jsonPayload = JsonSerializer.Serialize(requestPayload);
        var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

        // Send request to Ollama
        HttpResponseMessage response = await httpClient.PostAsync(OllamaApiUrl, content);

        if (!response.IsSuccessStatusCode)
        {
            string errorContent = await response.Content.ReadAsStringAsync();
            throw new Exception($"Ollama API error ({response.StatusCode}): {errorContent}");
        }

        // Parse response
        string responseContent = await response.Content.ReadAsStringAsync();
        var jsonResponse = JsonSerializer.Deserialize<JsonElement>(responseContent);

        // Extract the message content
        if (jsonResponse.TryGetProperty("message", out JsonElement messageElement) &&
            messageElement.TryGetProperty("content", out JsonElement contentElement))
        {
            return contentElement.GetString() ?? "No content returned";
        }

        throw new Exception("Unexpected response format from Ollama API");
    }
}
