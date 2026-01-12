# Image Object Detection using Ollama

A .NET console application that uses Ollama's vision model to detect and identify objects in images.

## Prerequisites

1. **.NET SDK 10.0** (or later) - Already installed ✓
2. **Ollama** - Needs to be installed (see Step 1 below)

## Step 1: Install Ollama

### Windows Installation

1. Download Ollama from: https://ollama.ai/download
2. Run the installer and follow the setup wizard
3. Verify installation by opening a terminal and running:
   ```powershell
   ollama --version
   ```

### Pull the Vision Model

After installing Ollama, you need to pull a vision model that can analyze images:

```powershell
ollama pull llava
```

This will download the LLaVA model (Large Language and Vision Assistant) which is capable of object detection in images.

**Note:** The first time you pull a model, it may take several minutes depending on your internet connection as the model files are large (several GB).

## Step 2: Build and Run the Application

### Build the application:

```powershell
cd ImageObjectDetection
dotnet build
```

### Run the application:

```powershell
dotnet run -- <path_to_image>
```

Or build a release version:

```powershell
dotnet publish -c Release
```

Then run the executable:

```powershell
.\bin\Release\net10.0\publish\ImageObjectDetection.exe <path_to_image>
```

### Example Usage:

Using test images (included in the project):
```powershell
dotnet run -- ".\test-images\test-ball.jpg"
dotnet run -- ".\test-images\test-book.jpg"
dotnet run -- ".\test-images\test-multiple.jpg"
dotnet run -- ".\test-images\test-simple.jpg"
```

Using your own images:
```powershell
dotnet run -- "C:\Users\YourName\Pictures\photo.jpg"
```

or with relative paths:
```powershell
dotnet run -- ".\test-image.png"
```

## How It Works

1. The application takes an image file path as a command-line argument
2. Reads the image file and converts it to base64 encoding
3. Sends the image to Ollama's API (running on `http://localhost:11434`)
4. Uses the LLaVA model to analyze the image and identify objects
5. Displays the detected objects in the console

## Troubleshooting

### Error: "Connection refused" or "Ollama API error"
- Make sure Ollama is running. You can start it by running `ollama serve` in a terminal, or it may start automatically as a service.

### Error: "model not found"
- Make sure you've pulled the model: `ollama pull llava`

### Error: "Image file not found"
- Check that the image path is correct and the file exists
- Use quotes around paths with spaces: `"C:\My Pictures\photo.jpg"`

## Alternative Models

You can modify the `DefaultModel` constant in `Program.cs` to use other vision models:

- `llava` - General purpose vision model (recommended)
- `llava:13b` - Larger, more accurate version
- `bakllava` - Alternative vision model

To use a different model, first pull it:
```powershell
ollama pull llava:13b
```

Then update the `DefaultModel` constant in `Program.cs`.
