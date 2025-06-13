from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ollama
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



@app.get("/generic/getinfo", response_class=HTMLResponse)
async def getinfo(request: Request):
    return templates.TemplateResponse("getinfogeneric.html", {"request": request})

@app.post("/qna/generic", response_class=HTMLResponse)
async def qna(request: Request):
    try:
        form_data = await request.form()
        user_answer = form_data.get("answer")
        name = form_data.get("name")
        role = form_data.get("role")
        experience = form_data.get("experience")

        if not (user_answer, (name, role, experience)):
            return templates.TemplateResponse(
            "error.html",
            {"request": request, "redirect1": "Direct access is not allowed, please fill the form first."}
            )

        elif not user_answer :
            prompt = str({'Name': {name}, 'role': {role}, 'years of experience': {experience}})
        else:
            prompt = user_answer
        question = generategeneric(prompt)

        if question.startswith("Error: Failed to generate question:"):
            return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": question}
        )

        else:
            with open("chat/QnA.json", 'r') as f:
                file = json.load(f)
            file[prompt] = question
                
            with open("chat/QnA.json", 'w') as f:
                json.dump(file, f)
            
            return templates.TemplateResponse(
                "generic.html",
                {"request": request, "question": question}
            )
        
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error: {str(e)}"}
        )

def generategeneric(prompt: str):
    with open("prompt/system_prompt.txt", 'r') as f:
        system_prompt = f.read()
    try:
        response = ollama.chat(
            model='phi3:3.8b',
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": system_prompt}
            ]
        )
        content = response['message']['content']
        content = content[::-1]
        start = content.find(''.join(reversed('</question>'))) + len(''.join(reversed('</question>')))
        end = start + content[start:].find(''.join(reversed('<question>')))
        content = content[start:end]
        content = content[::-1]
        return content

    except Exception as e:
        return f"Error: Failed to generate question: {str(e)}"    



@app.get("/technical/getinfo", response_class=HTMLResponse)
async def getinfo(request: Request):
    return templates.TemplateResponse("getinfotechnical.html", {"request": request})

@app.post("/qna/technical", response_class=HTMLResponse)
async def qna(request: Request):
    try:
        form_data = await request.form()
        user_answer = form_data.get("answer")
        name = form_data.get("name")
        role = form_data.get("role")
        experience = form_data.get("experience")
        
        if not (user_answer, (name, role, experience)):
            return templates.TemplateResponse(
            "error.html",
            {"request": request, "redirect2": "Direct access is not allowed, please fill the form first."}
            )
                
        elif not user_answer:
            prompt = str({'Name': {name}, 'role': {role}, 'years of experience': {experience}})
        else:
            prompt = user_answer
        mcq = generatetechnical(prompt)

        if isinstance(mcq, str):
            return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": mcq}
        )

        return templates.TemplateResponse(
                "technical.html",
                {"request": request, "mcq": mcq}
            )
        
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error (while handling the response): {str(e)}"}
        )
    
def generatetechnical(prompt: str):
    with open("prompt/system_prompt_mcq.txt", mode='r', encoding="utf-8", errors="ignore") as f:
        system_prompt = f.read()

    try:
        response = ollama.chat(
            model='deepseek-r1:8b',
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": system_prompt}
            ]
        )    
        content = response['message']['content']
        start_idx = content.find("</think>") + len("</think>")
        a = ''.join(content[start_idx:].split('\n'))
        final = json.loads(a)
        return final

    except Exception as e:
        return f"Error: Failed to generate mcq (error while generating): {str(e)}"
    



