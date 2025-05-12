from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from .firebase import auth, db
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        return RedirectResponse("/login", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # Firebase Admin SDK는 로그인 토큰 발급은 못하지만,
    # 프론트엔드에서 Firebase Client SDK로 로그인 후 토큰 검증하는 방식 추천
    return {"msg": "Login flow to be implemented via frontend or Firebase client SDK"}
