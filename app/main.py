from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models import Employee, MenuItem, RestaurantTable, Order

app = FastAPI(
    title="Restaurant Management System",
    description="Hệ thống quản lý nhà hàng",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def home(
    request: Request,
    db: Session = Depends(get_db)
):
    stats = {
        "menu_items": db.query(MenuItem).count(),
        "tables": db.query(RestaurantTable).count(),
        "orders": db.query(Order).count(),
        "employees": db.query(Employee).count(),
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "restaurant-management"
    }


Instrumentator().instrument(app).expose(app)