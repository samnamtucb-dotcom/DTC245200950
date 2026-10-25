from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default="staff")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="available")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    order_items = relationship(
        "OrderItem",
        back_populates="menu_item"
    )


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="available")

    orders = relationship(
        "Order",
        back_populates="table"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    table_id = Column(
        Integer,
        ForeignKey("restaurant_tables.id"),
        nullable=False
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    status = Column(String(30), nullable=False, default="pending")
    total_amount = Column(Float, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    table = relationship(
        "RestaurantTable",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship(
        "Order",
        back_populates="items"
    )

    menu_item = relationship(
        "MenuItem",
        back_populates="order_items"
    )