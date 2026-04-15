import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import (
    init_db,
    seed_data,
    get_all_inventory,
    get_low_stock,
    get_logs,
    add_product,
    use_product,
    delete_product,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DEVELOPER_PASSWORD = os.getenv("DEVELOPER_PASSWORD", "Dfgnmbxo1")


class ProductCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    location: str
    minimum: float = 0
    notes: str = ""


class ProductUse(BaseModel):
    product_id: int
    quantity: float


class LoginRequest(BaseModel):
    mode: str
    password: str | None = None


@app.on_event("startup")
def startup():
    init_db()
    seed_data()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/login")
async def login(payload: LoginRequest):
    if payload.mode == "user":
        return {"ok": True, "role": "user"}

    if payload.mode == "developer":
        if payload.password == DEVELOPER_PASSWORD:
            return {"ok": True, "role": "developer"}
        raise HTTPException(status_code=401, detail="סיסמה שגויה")

    raise HTTPException(status_code=400, detail="מצב התחברות לא תקין")


@app.get("/api/inventory")
async def inventory():
    return JSONResponse(get_all_inventory())


@app.get("/api/low-stock")
async def low_stock():
    return JSONResponse(get_low_stock())


@app.get("/api/logs")
async def logs():
    return JSONResponse(get_logs())


@app.post("/api/products")
async def create_product(product: ProductCreate):
    add_product(
        name=product.name,
        quantity=product.quantity,
        unit=product.unit,
        location=product.location,
        minimum=product.minimum,
        notes=product.notes,
    )
    return {"ok": True}


@app.post("/api/use")
async def use_product_api(payload: ProductUse):
    success, message = use_product(payload.product_id, payload.quantity)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"ok": True}


@app.delete("/api/products/{product_id}")
async def delete_product_api(product_id: int):
    success = delete_product(product_id)

    if not success:
        raise HTTPException(status_code=404, detail="המוצר לא נמצא")

    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"status": "ok"}