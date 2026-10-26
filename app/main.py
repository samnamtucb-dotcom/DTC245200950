from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Employee,
    MenuItem,
    RestaurantTable,
    Order,
    OrderItem,
)


app = FastAPI(
    title="Restaurant Management System",
    description="Hệ thống quản lý nhà hàng",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# =========================================================
# DASHBOARD
# =========================================================

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


# =========================================================
# MENU - LIST
# =========================================================

@app.get("/menu")
async def menu_page(
    request: Request,
    db: Session = Depends(get_db)
):
    menu_items = (
        db.query(MenuItem)
        .order_by(MenuItem.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        "menu.html",
        {
            "request": request,
            "menu_items": menu_items
        }
    )


# =========================================================
# MENU - CREATE FORM
# =========================================================

@app.get("/menu/new")
async def new_menu_item_page(
    request: Request
):
    return templates.TemplateResponse(
        "menu_form.html",
        {
            "request": request,
            "item": None
        }
    )


# =========================================================
# MENU - CREATE
# =========================================================

@app.post("/menu/new")
async def create_menu_item(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    name = name.strip()
    category = category.strip()
    description = description.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Tên món ăn không được để trống."
        )

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Danh mục không được để trống."
        )

    if price < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá món ăn không được nhỏ hơn 0."
        )

    existing_item = (
        db.query(MenuItem)
        .filter(MenuItem.name.ilike(name))
        .first()
    )

    if existing_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Tên món ăn đã tồn tại trong thực đơn."
        )

    new_item = MenuItem(
        name=name,
        category=category,
        price=price,
        description=description or None,
        status="available"
    )

    db.add(new_item)
    db.commit()

    return RedirectResponse(
        url="/menu?created=1",
        status_code=303
    )


# =========================================================
# MENU - EDIT FORM
# =========================================================

@app.get("/menu/{item_id}/edit")
async def edit_menu_item_page(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    item = (
        db.query(MenuItem)
        .filter(MenuItem.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy món ăn."
        )

    return templates.TemplateResponse(
        "menu_form.html",
        {
            "request": request,
            "item": item
        }
    )


# =========================================================
# MENU - EDIT
# =========================================================

@app.post("/menu/{item_id}/edit")
async def update_menu_item(
    item_id: int,
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    item = (
        db.query(MenuItem)
        .filter(MenuItem.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy món ăn."
        )

    name = name.strip()
    category = category.strip()
    description = description.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Tên món ăn không được để trống."
        )

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Danh mục không được để trống."
        )

    if price < 0:
        raise HTTPException(
            status_code=400,
            detail="Giá món ăn không được nhỏ hơn 0."
        )

    duplicate_item = (
        db.query(MenuItem)
        .filter(
            MenuItem.name.ilike(name),
            MenuItem.id != item_id
        )
        .first()
    )

    if duplicate_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Tên món ăn đã được sử dụng bởi món khác."
        )

    item.name = name
    item.category = category
    item.price = price
    item.description = description or None

    db.commit()

    return RedirectResponse(
        url="/menu?updated=1",
        status_code=303
    )


# =========================================================
# MENU - DISABLE
# =========================================================

@app.post("/menu/{item_id}/disable")
async def disable_menu_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(MenuItem)
        .filter(MenuItem.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy món ăn."
        )

    item.status = "unavailable"

    db.commit()

    return RedirectResponse(
        url="/menu?disabled=1",
        status_code=303
    )


# =========================================================
# MENU - ENABLE
# =========================================================

@app.post("/menu/{item_id}/enable")
async def enable_menu_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = (
        db.query(MenuItem)
        .filter(MenuItem.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy món ăn."
        )

    item.status = "available"

    db.commit()

    return RedirectResponse(
        url="/menu?enabled=1",
        status_code=303
    )


# =========================================================
# TABLES
# =========================================================

@app.get("/tables")
async def tables_page(
    request: Request,
    db: Session = Depends(get_db)
):
    tables = (
        db.query(RestaurantTable)
        .order_by(RestaurantTable.table_number.asc())
        .all()
    )

    return templates.TemplateResponse(
        "tables.html",
        {
            "request": request,
            "tables": tables
        }
    )


# =========================================================
# ORDERS - LIST
# =========================================================

@app.get("/orders")
async def orders_page(
    request: Request,
    db: Session = Depends(get_db)
):
    orders = (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "orders": orders
        }
    )


# =========================================================
# ORDERS - CREATE FORM
# =========================================================

@app.get("/orders/new")
async def new_order_page(
    request: Request,
    db: Session = Depends(get_db)
):
    tables = (
        db.query(RestaurantTable)
        .order_by(RestaurantTable.table_number.asc())
        .all()
    )

    employees = (
        db.query(Employee)
        .order_by(Employee.name.asc())
        .all()
    )

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.status == "available")
        .order_by(MenuItem.name.asc())
        .all()
    )

    return templates.TemplateResponse(
        "new_order.html",
        {
            "request": request,
            "tables": tables,
            "employees": employees,
            "menu_items": menu_items
        }
    )


# =========================================================
# ORDERS - CREATE
# =========================================================

@app.post("/orders/new")
async def create_order(
    table_id: int = Form(...),
    employee_id: int = Form(...),
    menu_item_name: str = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    if quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="Số lượng phải lớn hơn hoặc bằng 1."
        )

    menu_item_name = menu_item_name.strip()

    if not menu_item_name:
        raise HTTPException(
            status_code=400,
            detail="Tên món ăn không được để trống."
        )

    table = (
        db.query(RestaurantTable)
        .filter(RestaurantTable.id == table_id)
        .first()
    )

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    menu_item = (
        db.query(MenuItem)
        .filter(MenuItem.name.ilike(menu_item_name))
        .first()
    )

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy bàn."
        )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhân viên."
        )

    if menu_item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy món ăn trong thực đơn."
        )

    if menu_item.status != "available":
        raise HTTPException(
            status_code=400,
            detail="Món ăn hiện không khả dụng."
        )

    total_amount = menu_item.price * quantity

    new_order = Order(
        table_id=table.id,
        employee_id=employee.id,
        status="pending",
        total_amount=total_amount
    )

    db.add(new_order)
    db.flush()

    new_order_item = OrderItem(
        order_id=new_order.id,
        menu_item_id=menu_item.id,
        quantity=quantity,
        unit_price=menu_item.price
    )

    db.add(new_order_item)
    db.commit()

    return RedirectResponse(
        url="/orders?created=1",
        status_code=303
    )


# =========================================================
# ORDERS - COMPLETE
# =========================================================

@app.post("/orders/{order_id}/complete")
async def complete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng."
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể hoàn thành đơn hàng đang chờ xử lý."
        )

    order.status = "completed"
    db.commit()

    return RedirectResponse(
        url="/orders?completed=1",
        status_code=303
    )


# =========================================================
# ORDERS - CANCEL
# =========================================================

@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng."
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể hủy đơn hàng đang chờ xử lý."
        )

    order.status = "cancelled"
    db.commit()

    return RedirectResponse(
        url="/orders?cancelled=1",
        status_code=303
    )


# =========================================================
# EMPLOYEES
# =========================================================

@app.get("/employees")
async def employees_page(
    request: Request,
    db: Session = Depends(get_db)
):
    employees = (
        db.query(Employee)
        .order_by(Employee.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        "employees.html",
        {
            "request": request,
            "employees": employees
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "restaurant-management"
    }


# =========================================================
# PROMETHEUS METRICS
# =========================================================

Instrumentator().instrument(app).expose(app)