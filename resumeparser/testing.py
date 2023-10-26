from fastapi.responses import HTMLResponse
import spacy
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

nlp = spacy.load("./model/model-best")

templates = Jinja2Templates(directory="template")


def get_ents(text):
    doc = nlp(text)
    res = []

    for ent in doc.ents:
        res.append({"label": ent.label_, "value": ent.text})
    return res


# API to expose model

# flask
# flask_restx
# fast_api

# client UI (html+css+js)
# UI => file(resume) / text => API => model => ents => UI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/resumeparser")
def process_resume_text(text: str):
    res = get_ents(text)
    return res


@app.get("/", response_class=HTMLResponse)
def home(req: Request):
    return templates.TemplateResponse("index.html", {"request": req})


# uvicorn testing:app --reload