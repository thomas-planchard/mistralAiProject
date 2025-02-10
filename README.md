# Mistral Maestro

Mistral Maestro is a FastAPI-based tool that reviews, optimizes, and provides suggestions for improving Python code snippets using Mistral API. It validates code syntax and, if valid, sends the code to the AI for analysis. The results are then rendered on a web page using a custom HTML template that features:

- A **CodeMirror** code editor for the input.
- **Markdown rendering** of the AI suggestions.
- **Syntax-highlighted, read-only code blocks** with copy-to-clipboard functionality in the analysis output.

## Features

- **Syntax Validation**  
  Uses Python's built-in `ast` module to validate code syntax before analysis.

- **AI Analysis via Mistral API**  
  Sends a prompt (including the user's code) to the Mistral API to receive analysis and suggestions for performance and security improvements.

- **Enhanced User Interface**  
  - **CodeMirror** is used for the input editor to provide a modern, syntax-highlighted experience.
  - The analysis output is rendered from Markdown into HTML using **marked**, and any code blocks are further styled and made interactive with a copy button.

## Prerequisites
- **Python 3.8+** (tested with Python 3.12)
- **pip** for package management
- A valid **Mistral API key**

## Installation

1. **Clone the Repository**

```bash
git clone <repository-url>
cd <repository-directory>
```

2.	**Set Up a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate
```

3.	**Install Dependencies**

Use the requirements.txt file to install all required packages:

```bash
pip install -r requirements.txt
```

4.	**Configure Environment Variables**

Set your Mistral API key as an environment variable. For example, on Unix-like systems:

```bash
export MISTRAL_API_KEY="your_mistral_api_key_here"
```


## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

Then, open your web browser and navigate to:
http://127.0.0.1:8000/


## How It Works

1.	**User Input**

The user pastes a Python code snippet into the editor on the homepage.

2.	**Syntax Validation**

The backend uses Python’s ast.parse to check the code for syntax errors.
    
-	If errors are found, an error message is displayed.
-	Otherwise, it proceeds to analyze the code.

3.	**AI Analysis**

A prompt is constructed that includes the user’s code and is sent to the Mistral API via an asynchronous HTTP request (using httpx).

The API returns suggestions on potential performance or security issues and improvements.

4.	**Rendering the Response**

The returned suggestions (in Markdown format) are:
-	Converted into HTML using the marked library.
-	Injected into the HTML template.
-	Enhanced further by transforming code blocks into read-only CodeMirror instances with a copy-to-clipboard button.


## File Structure
-	main.py
    
    Contains the FastAPI application. It:
	-	Validates Python code using the ast module.
	-	Prepares a prompt and calls the Mistral API.
	-	Renders the index.html template with the analysis results.

-	templates/index.html
    
    The HTML template used to render the homepage. It:
	-	Provides the editor for code input.
	-	Displays analysis results (rendered from Markdown).


