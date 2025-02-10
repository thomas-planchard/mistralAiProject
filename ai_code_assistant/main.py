import os
import ast
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Initialize FastAPI and the Jinja2 template directory
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load your Mistral API credentials from an environment variable
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# Replace with the actual endpoint provided by Mistral
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # <-- update as needed

async def call_mistral_api(prompt: str) -> str:
    headers = {
         "Authorization": f"Bearer {MISTRAL_API_KEY}",
         "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",  # Adjust the model name as needed
         # Send the prompt in the expected 'messages' field as a list of message objects.
         "messages": [
             {"role": "user", "content": prompt}
         ],
         "temperature": 0.7,     # Adjust temperature for creativity
         # Add any additional parameters required by the API here.
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
         response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
         if response.status_code != 200:
             # In a production app, implement better error handling/logging.
             return f"Error: {response.status_code} - {response.text}"
         data = response.json()
         # Depending on the response structure, adjust how you extract the generated message.
         # For example, if the API returns a chat-style completion:
         if "choices" in data:
             # Assuming the response has a choices list with messages.
             return data["choices"][0]["message"].get("content", "No content returned.")
         # Fallback if the API still uses a simpler structure:
         return data.get("completion", "No completion returned.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renders the homepage with a code input form.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_code(request: Request, code_snippet: str = Form(...)):
    """
    Receives a code snippet, validates its syntax, sends it for analysis
    to the Mistral API, and returns the results.
    """
    analysis = {}
    
    # 1. Validate Syntax
    try:
         ast.parse(code_snippet)
         analysis["syntax_valid"] = True
    except SyntaxError as e:
         analysis["syntax_valid"] = False
         analysis["syntax_error"] = str(e)
    
    if not analysis["syntax_valid"]:
         # If syntax errors exist, return early with the error message.
         analysis["suggestions"] = "Please fix the syntax errors before further analysis."
         return templates.TemplateResponse("index.html", {"request": request, "analysis": analysis, "code_snippet": code_snippet})
    
    # 2. Prepare the Prompt for the Mistral API
    prompt = (
         "Analyze the following Python code snippet for any potential performance "
         "and security issues. Provide suggestions on how to optimize and improve it. "
         "Here is the code:\n\n"
         f"{code_snippet}\n\n"
         "Please provide a detailed review and recommendations."
    )
    
    # 3. Call the Mistral API to obtain suggestions
    completion = await call_mistral_api(prompt)
    analysis["suggestions"] = completion
    
    return templates.TemplateResponse("index.html", {"request": request, "analysis": analysis, "code_snippet": code_snippet})