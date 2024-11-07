# Fact.AI - A Fact-Checking AI with Wikipedia Integration

**Fact.AI** is a Python-based fact-checking application that combines the power of AI models with Wikipedia to provide up-to-date, reliable information. The application uses multiple AI models to verify facts, along with Wikipedia summaries as a source of real-time information.

## Features

- **Multi-Model Fact Checking**: Utilizes multiple AI models to cross-verify facts, with final evaluation for reliability.
- **Wikipedia Integration**: Automatically retrieves Wikipedia summaries to provide up-to-date information as context for fact-checking.
- **User-Friendly GUI**: Developed with Tkinter, including light and dark themes.
- **API Key Management**: Easily add, remove, or update your API key through the settings.

## Installation

### Prerequisites

- **Python 3.6+**: Ensure Python is installed on your system if you are running the Python script directly.
- **Dependencies**: The required libraries are listed in `requirements.txt`. They can be installed with:

Install requirements to run Main.py
  ```bash pip install -r requirements.txt```

## Key Libraries
- wikipedia-api: To retrieve real-time summaries from Wikipedia.
- tkinter: For creating the graphical user interface.
- groq: For AI model interactions (requires an API key).

## Clone the Repository
```git clone https://github.com/yourusername/FactAI.git```
```cd FactAI```

### Usage
Running the Application: You can run the fact-checking AI directly by double-clicking FactAI.exe located in the dist folder.

## Running Directly from Python (Alternative)
```python Main.py```

## Error Handling
- API Key Missing: If the API key is not set, Fact.AI will prompt you to enter it in Settings.
- Rate Limits: If the Groq API rate limit is exceeded, Fact.AI will pause and retry after the specified time.

### Acknowledgments
- Groq for AI models.
- Wikipedia for providing a comprehensive API for real-time information.

## Contributing
Feel free to open issues or submit pull requests to contribute to the project. Ensure all contributions follow the repository's code style and structure.


