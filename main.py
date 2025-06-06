from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ollama

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/getinfo", response_class=HTMLResponse)
async def getinfo(request: Request):
    return templates.TemplateResponse("getinfo.html", {"request": request})

@app.get("/processing", response_class=HTMLResponse)
async def processing(request: Request):
    return templates.TemplateResponse("underprocess.html", {"request": request})

@app.get("/generic", response_class=HTMLResponse)
async def generic(request: Request):
    return templates.TemplateResponse("generic.html", {"request": request})

@app.get("/show", response_class=HTMLResponse)
async def show(request: Request):
    name = request.query_params.get("name")
    role = request.query_params.get("role")
    experience = request.query_params.get("experience")
    return templates.TemplateResponse("generic.html", {"request": request})

@app.post("/qna", response_class=HTMLResponse)
async def qna(request: Request):
    try:
        form_data = await request.form()
        user_answer = form_data.get("answer")
        name = form_data.get("name")
        role = form_data.get("role")
        experience = form_data.get("experience")

        if not user_answer:
            prompt = f"Hey I am {name},applying for {role} role and I have {experience} years of experience"
        else:
            prompt = user_answer

        question = generate(prompt)

        return templates.TemplateResponse(
            "generic.html",
            {"request": request, "question": question}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "generic.html",
            {"request": request, "question": f"Error: {str(e)}"}
        )
    

def generate(prompt: str):
    with open("prompt/sys_prompt.txt", 'r') as f:
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
        content = content[::-1]
        start = content.find(''.join(reversed('</answer>'))) + len(''.join(reversed('?</answer>')))
        end = start + content[start:].find(''.join(reversed('<answer>')))
        content = content[start:end]
        content = content[::-1]

        print(content)

        return content

    except Exception as e:
        return f"Error: Failed to generate question: {str(e)}"