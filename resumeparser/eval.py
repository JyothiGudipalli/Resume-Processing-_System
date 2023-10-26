from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import spacy
from fastapi.middleware.cors import CORSMiddleware


nlp = spacy.load("./model/model-best")

app = FastAPI()

templates = Jinja2Templates(directory="template")

def get_ents(text):
    doc = nlp(text)
    res = []

    for ent in doc.ents:
        res.append({"label": ent.label_, "value": ent.text})
    return res
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/resumeparser")
async def process_resume_file(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None)
):
    if resume_file:
        resume_content = await resume_file.read()
    elif resume_text:
        resume_content = resume_text
    else:
        return []

    res = get_ents(resume_content)
    return res

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
