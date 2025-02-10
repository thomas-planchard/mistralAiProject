import os
import ast
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# -----------------------------------------------------------------------------
# App Initialization and Configuration
# -----------------------------------------------------------------------------

# Initialize the FastAPI application.
app = FastAPI()

# Configure the directory for Jinja2 templates.
templates = Jinja2Templates(directory="templates")

# Load Mistral API credentials and endpoint URL from environment variables.
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # Update as needed.

# -----------------------------------------------------------------------------
# Mistral API Call Function
# -----------------------------------------------------------------------------

async def call_mistral_api(prompt: str) -> str:
    """
    Call the Mistral API with a prompt and return the AI-generated response.

    Args:
        prompt (str): The input prompt to be analyzed.

    Returns:
        str: The generated message from the API or an error message if the call fails.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",  # Adjust the model name as needed.
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,  # Adjust temperature to control creativity.
        # Add any additional parameters required by the API.
    }
    
    # Create an HTTPX async client with a timeout.
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            # In production, you may want to log this error or raise an exception.
            return f"Error: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # If the API returns a chat-style response with a choices list, extract the first message.
        if "choices" in data:
            return data["choices"][0]["message"].get("content", "No content returned.")
        
        # Fallback extraction if the API returns a simpler structure.
        return data.get("completion", "No completion returned.")

# -----------------------------------------------------------------------------
# FastAPI Endpoints
# -----------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Render the homepage with the code input form.
    
    Args:
        request (Request): The incoming request object.
    
    Returns:
        HTMLResponse: The rendered HTML template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_code(request: Request, code_snippet: str = Form(...)):
    """
    Analyze a given Python code snippet by validating its syntax and sending it to the Mistral API for review.

    Steps:
    1. Validate the syntax of the provided Python code.
    2. If syntax errors exist, return an error message.
    3. Otherwise, prepare a prompt to analyze the code for performance and security issues.
    4. Call the Mistral API with the prompt.
    5. Render the results on the homepage.

    Args:
        request (Request): The incoming request object.
        code_snippet (str): The Python code to analyze.

    Returns:
        HTMLResponse: The rendered HTML template with analysis results.
    """
    analysis = {}

    # Step 1: Validate the syntax of the code snippet.
    try:
        ast.parse(code_snippet)
        analysis["syntax_valid"] = True
    except SyntaxError as e:
        analysis["syntax_valid"] = False
        analysis["syntax_error"] = str(e)
    
    # Step 2: If there is a syntax error, return immediately with an error message.
    if not analysis["syntax_valid"]:
        analysis["suggestions"] = "Please fix the syntax errors before further analysis."
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "analysis": analysis, "code_snippet": code_snippet}
        )
    
    # Step 3: Prepare a prompt for performance and security analysis.
    prompt = (
        "Analyze the following Python code snippet for any potential performance and security issues. "
        "Provide suggestions on how to optimize and improve it. Here is the code:\n\n"
        f"{code_snippet}\n\n"
        "Please provide a detailed review and recommendations."
    )
    
    # Step 4: Call the Mistral API and store the response.
    completion = await call_mistral_api(prompt)
    analysis["suggestions"] = completion

    # Step 5: Render the template with the analysis results.
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "analysis": analysis, "code_snippet": code_snippet}
    )