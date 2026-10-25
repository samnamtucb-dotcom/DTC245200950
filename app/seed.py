from app.database import SessionLocal
from app.models import Employee, MenuItem, RestaurantTable, Order, OrderItem


def seed_database():
    db = SessionLocal()

    try:
        # Không seed lại nếu database đã có dữ liệu
        if db.query(Employee).count() > 0:
            print("Database already contains seed data.")
            return

        # Nhân viên
        employees = [
            Employee(
                name="Nguyen Van An",
                username="an.manager",
                role="manager"
            ),
            Employee(
                name="Tran Minh Binh",
                username="binh.staff",
                role="staff"
            ),
            Employee(
                name="Le Thu Ha",
                username="ha.cashier",
                role="cashier"
            ),
        ]

        # Món ăn
        menu_items = [
            MenuItem(
                name="Pho Bo",
                category="Main",
                price=55000,
                description="Pho bo truyen thong"
            ),
            MenuItem(
                name="Com Ga",
                category="Main",
                price=50000,
                description="Com ga"
            ),
            MenuItem(
                name="Bun Cha",
                category="Main",
                price=45000,
                description="Bun cha"
            ),
            MenuItem(
                name="Tra Chanh",
                category="Drink",
                price=20000,
                description="Tra chanh mat"
            ),
            MenuItem(
                name="Ca Phe Sua",
                category="Drink",
                price=30000,
                description="Ca phe sua"
            ),
            MenuItem(
                name="Nuoc Cam",
                category="Drink",
                price=30000,
                description="Nuoc cam"
            ),
        ]

        # Bàn ăn
        tables = [
            RestaurantTable(table_number=1, capacity=2),
            RestaurantTable(table_number=2, capacity=4),
            RestaurantTable(table_number=3, capacity=4),
            RestaurantTable(table_number=4, capacity=6),
            RestaurantTable(table_number=5, capacity=8),
        ]

        db.add_all(employees + menu_items + tables)
        db.flush()

        # Một đơn hàng mẫu
        order = Order(
            table_id=tables[1].id,
            employee_id=employees[1].id,
            status="completed",
            total_amount=130000
        )

        db.add(order)
        db.flush()

        order_items = [
            OrderItem(
                order_id=order.id,
                menu_item_id=menu_items[0].id,
                quantity=2,
                unit_price=55000
            ),
            OrderItem(
                order_id=order.id,
                menu_item_id=menu_items[3].id,
                quantity=1,
                unit_price=20000
            ),
        ]

        db.add_all(order_items)
        db.commit()

        print("Seed data created successfully.")

    except Exception as error:
        db.rollback()
        print(f"Seed failed: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()