from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, Request,Form
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import spacy
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="template")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["data"]
users_collection = db["collect"]

# Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def registration_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(None),
    gender: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "gender": gender,
        "phone_number": phone_number,
        "email": email,
        "password": password
    }
    users_collection.insert_one(user_data)

    # Redirect to the Login page
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def registration_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Registration Endpoint
@app.post("/login", response_class=HTMLResponse)
async def login_user(
    username: str = Form(...),
    password: str = Form(...),
):
    # Perform user registration logic (simplified for demonstration)
    users_collection.insert_one({"username": username, "password": password})

    # Redirect to the Login page
    return RedirectResponse(url="/home")

nlp = spacy.load("./model/model-best")
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


@app.get("/resumeparser")
def process_resume_text(text: str):
    res = get_ents(text)
    return res


@app.get("/index", response_class=HTMLResponse)
def home(req: Request):
    return templates.TemplateResponse("home.html", {"request": req})


