"""
Run this once after starting MongoDB to populate AutoTrade with realistic
sample data for demonstration and viva purposes.

    python seed_data.py
"""
import random
from datetime import datetime, timedelta, timezone

from database.mongodb import (
    get_collection, create_indexes,
    CARS, SELLERS, CUSTOMERS, INSPECTIONS, ENQUIRIES,
    TEST_DRIVES, SALES, PAYMENTS, OWNERSHIP_TRANSFERS, EMPLOYEES,
)
from services.valuation import calculate_valuation
from services.profit import calculate_sale_profit

random.seed(42)
NOW = datetime.now(timezone.utc)


def days_ago(n):
    return NOW - timedelta(days=n)


def reset_collections():
    for name in (CARS, SELLERS, CUSTOMERS, INSPECTIONS, ENQUIRIES,
                 TEST_DRIVES, SALES, PAYMENTS, OWNERSHIP_TRANSFERS, EMPLOYEES):
        get_collection(name).delete_many({})


def seed_sellers():
    sellers = [
        {"seller_id": "SEL001", "name": "Ramesh Iyer", "phone": "9840012345",
         "email": "ramesh.iyer@gmail.com", "address": "Anna Nagar, Chennai",
         "seller_type": "Individual", "registration_date": days_ago(200)},
        {"seller_id": "SEL002", "name": "Priya Motors", "phone": "9884023456",
         "email": "contact@priyamotors.in", "address": "T. Nagar, Chennai",
         "seller_type": "Dealer", "registration_date": days_ago(180)},
        {"seller_id": "SEL003", "name": "Suresh Kumar", "phone": "9944034567",
         "email": "suresh.kumar@yahoo.com", "address": "Nagercoil, Tamil Nadu",
         "seller_type": "Individual", "registration_date": days_ago(150)},
        {"seller_id": "SEL004", "name": "Trichy Auto Traders", "phone": "9894045678",
         "email": "sales@trichyauto.com", "address": "Trichy, Tamil Nadu",
         "seller_type": "Company", "registration_date": days_ago(120)},
        {"seller_id": "SEL005", "name": "Lakshmi Narayanan", "phone": "9791056789",
         "email": "lakshmi.n@gmail.com", "address": "Madurai, Tamil Nadu",
         "seller_type": "Individual", "registration_date": days_ago(90)},
    ]
    get_collection(SELLERS).insert_many(sellers)
    return sellers


def seed_employees():
    employees = [
        {"employee_id": "EMP001", "name": "Arun Kumar", "phone": "9003011111",
         "email": "arun.kumar@autotrade.in", "role": "Admin", "joining_date": "2022-01-10"},
        {"employee_id": "EMP002", "name": "Divya Shree", "phone": "9003022222",
         "email": "divya.shree@autotrade.in", "role": "Sales Executive", "joining_date": "2022-06-15"},
        {"employee_id": "EMP003", "name": "Karthik Raja", "phone": "9003033333",
         "email": "karthik.raja@autotrade.in", "role": "Sales Executive", "joining_date": "2023-02-01"},
        {"employee_id": "EMP004", "name": "Meena Rani", "phone": "9003044444",
         "email": "meena.rani@autotrade.in", "role": "Inspector", "joining_date": "2022-09-20"},
        {"employee_id": "EMP005", "name": "Vignesh Babu", "phone": "9003055555",
         "email": "vignesh.babu@autotrade.in", "role": "Manager", "joining_date": "2021-11-05"},
    ]
    get_collection(EMPLOYEES).insert_many(employees)
    return employees


def seed_customers():
    customers = [
        {"customer_id": "CUS001", "name": "Anitha Raj", "phone": "9600011111", "email": "anitha.raj@gmail.com",
         "address": "Nagercoil", "preferred_brand": "Hyundai", "preferred_fuel_type": "Petrol",
         "max_budget": 700000, "created_at": days_ago(60)},
        {"customer_id": "CUS002", "name": "Dinesh Kumar", "phone": "9600022222", "email": "dinesh.kumar@gmail.com",
         "address": "Nagercoil", "preferred_brand": "Maruti Suzuki", "preferred_fuel_type": "Petrol",
         "max_budget": 500000, "created_at": days_ago(58)},
        {"customer_id": "CUS003", "name": "Priyanka S", "phone": "9600033333", "email": "priyanka.s@gmail.com",
         "address": "Trivandrum", "preferred_brand": "Honda", "preferred_fuel_type": "Petrol",
         "max_budget": 800000, "created_at": days_ago(55)},
        {"customer_id": "CUS004", "name": "Mohammed Faizal", "phone": "9600044444", "email": "faizal.m@gmail.com",
         "address": "Tirunelveli", "preferred_brand": "Toyota", "preferred_fuel_type": "Diesel",
         "max_budget": 1200000, "created_at": days_ago(50)},
        {"customer_id": "CUS005", "name": "Kavya Lakshmi", "phone": "9600055555", "email": "kavya.l@gmail.com",
         "address": "Madurai", "preferred_brand": "Tata", "preferred_fuel_type": "CNG",
         "max_budget": 600000, "created_at": days_ago(45)},
        {"customer_id": "CUS006", "name": "Selvam R", "phone": "9600066666", "email": "selvam.r@gmail.com",
         "address": "Chennai", "preferred_brand": "Kia", "preferred_fuel_type": "Petrol",
         "max_budget": 900000, "created_at": days_ago(40)},
        {"customer_id": "CUS007", "name": "Fathima Beevi", "phone": "9600077777", "email": "fathima.b@gmail.com",
         "address": "Nagercoil", "preferred_brand": "Mahindra", "preferred_fuel_type": "Diesel",
         "max_budget": 1000000, "created_at": days_ago(30)},
        {"customer_id": "CUS008", "name": "Gowtham Sundar", "phone": "9600088888", "email": "gowtham.s@gmail.com",
         "address": "Coimbatore", "preferred_brand": "Volkswagen", "preferred_fuel_type": "Petrol",
         "max_budget": 850000, "created_at": days_ago(25)},
    ]
    get_collection(CUSTOMERS).insert_many(customers)
    return customers


def _condition(engine, body, tyre, interior, accident, service):
    score = round((engine + body + tyre + interior) / 4, 2)
    label = "Excellent" if score >= 8.5 else "Good" if score >= 7 else "Fair" if score >= 5 else "Poor"
    return {
        "engine_condition": engine, "body_condition": body, "tyre_condition": tyre,
        "interior_condition": interior, "accident_history": accident, "service_history": service,
        "overall_condition": label, "inspection_score": score,
    }


def seed_cars(sellers):
    car_specs = [
        ("Hyundai", "i20", "Asta", 2020, "Petrol", "Manual", 32000, "White", 2020, 1, 620000, 15000, 5000, "Available"),
        ("Maruti Suzuki", "Swift", "VXi", 2019, "Petrol", "Manual", 41000, "Red", 2019, 1, 480000, 12000, 4000, "Available"),
        ("Honda", "City", "V", 2021, "Petrol", "Automatic", 22000, "Silver", 2021, 1, 950000, 8000, 3000, "Available"),
        ("Toyota", "Innova Crysta", "GX", 2018, "Diesel", "Manual", 68000, "Grey", 2018, 2, 1350000, 25000, 8000, "Reserved"),
        ("Kia", "Seltos", "HTX", 2022, "Petrol", "Automatic", 15000, "Blue", 2022, 1, 1250000, 5000, 2000, "Available"),
        ("Tata", "Nexon", "XZ+", 2020, "Diesel", "Manual", 38000, "White", 2020, 1, 780000, 10000, 4000, "Sold"),
        ("Mahindra", "XUV500", "W10", 2017, "Diesel", "Manual", 82000, "Black", 2017, 2, 950000, 30000, 9000, "Sold"),
        ("Volkswagen", "Polo", "Highline", 2019, "Petrol", "Manual", 45000, "White", 2019, 1, 560000, 14000, 5000, "Sold"),
        ("Skoda", "Rapid", "Ambition", 2018, "Petrol", "Automatic", 51000, "Grey", 2018, 2, 520000, 18000, 6000, "Sold"),
        ("Hyundai", "Creta", "SX", 2021, "Diesel", "Automatic", 27000, "Blue", 2021, 1, 1400000, 9000, 3000, "Sold"),
        ("Maruti Suzuki", "Baleno", "Zeta", 2020, "Petrol", "Manual", 34000, "Red", 2020, 1, 610000, 11000, 4000, "Sold"),
        ("Honda", "Amaze", "VX", 2019, "Petrol", "Manual", 39000, "Silver", 2019, 1, 570000, 13000, 4500, "Sold"),
        ("Toyota", "Glanza", "G", 2021, "Petrol", "Manual", 18000, "White", 2021, 1, 680000, 6000, 2500, "Sold"),
        ("Tata", "Altroz", "XZ", 2022, "Petrol", "Manual", 12000, "Blue", 2022, 1, 640000, 4000, 2000, "Under Inspection"),
        ("Kia", "Sonet", "HTK+", 2021, "Diesel", "Manual", 24000, "Grey", 2021, 1, 830000, 7000, 3000, "Maintenance"),
    ]
    conditions = [
        (9, 8, 7, 9, False, True), (7, 7, 6, 7, False, True), (9, 9, 8, 9, False, True),
        (6, 6, 5, 6, True, False), (9, 9, 9, 9, False, True), (8, 7, 7, 8, False, True),
        (5, 5, 4, 5, True, True), (7, 6, 6, 7, False, True), (6, 6, 5, 6, True, True),
        (8, 8, 7, 8, False, True), (8, 7, 7, 8, False, True), (7, 7, 6, 7, False, True),
        (9, 8, 8, 9, False, True), (9, 9, 9, 9, False, True), (7, 6, 6, 7, False, False),
    ]

    cars = []
    seller_cycle = [s["seller_id"] for s in sellers]
    for i, spec in enumerate(car_specs):
        (brand, model, variant, year, fuel, transmission, mileage, color, reg_year,
         owners, purchase, repair, other, status) = spec
        engine, body, tyre, interior, accident, service = conditions[i]

        car = {
            "car_id": f"CAR{i + 1:03d}",
            "brand": brand, "model": model, "variant": variant,
            "manufacturing_year": year, "fuel_type": fuel, "transmission": transmission,
            "mileage": mileage, "color": color, "registration_year": reg_year,
            "previous_owners": owners, "seller_id": seller_cycle[i % len(seller_cycle)],
            "pricing": {
                "purchase_price": purchase, "repair_cost": repair, "other_expenses": other,
                "selling_price": 0, "estimated_market_value": 0, "expected_profit": 0,
            },
            "condition": _condition(engine, body, tyre, interior, accident, service),
            "status": status,
            "created_at": days_ago(90 - i * 3),
        }
        valuation = calculate_valuation(car)
        car["pricing"]["estimated_market_value"] = valuation["estimated_market_value"]
        car["pricing"]["selling_price"] = valuation["recommended_selling_price"]
        car["pricing"]["expected_profit"] = valuation["expected_profit"]
        cars.append(car)

    get_collection(CARS).insert_many(cars)
    return cars


def seed_inspections(cars, employees):
    inspectors = [e["employee_id"] for e in employees if e["role"] in ("Inspector", "Manager")]
    inspections = []
    for i, car in enumerate(cars[:8]):
        c = car["condition"]
        inspections.append({
            "inspection_id": f"INS{i + 1:03d}",
            "car_id": car["car_id"],
            "inspection_date": days_ago(85 - i * 3),
            "inspector_id": inspectors[i % len(inspectors)],
            "engine_condition": c["engine_condition"], "body_condition": c["body_condition"],
            "tyre_condition": c["tyre_condition"], "interior_condition": c["interior_condition"],
            "electrical_condition": c["engine_condition"] - 0.5 if c["engine_condition"] > 1 else 1,
            "accident_history": c["accident_history"], "service_history": c["service_history"],
            "overall_score": c["inspection_score"],
            "remarks": "Minor wear and tear noted" if c["inspection_score"] < 7 else "Well maintained vehicle",
        })
    get_collection(INSPECTIONS).insert_many(inspections)


def seed_enquiries(cars, customers):
    active_cars = [c for c in cars if c["status"] != "Sold"]
    enquiries = []
    for i in range(10):
        car = active_cars[i % len(active_cars)]
        customer = customers[i % len(customers)]
        statuses = ["New", "Contacted", "Follow-up", "Converted", "Closed"]
        enquiries.append({
            "enquiry_id": f"ENQ{i + 1:03d}",
            "customer_id": customer["customer_id"], "car_id": car["car_id"],
            "enquiry_date": days_ago(40 - i * 2),
            "message": f"Interested in the {car['brand']} {car['model']}, is it still available?",
            "status": statuses[i % len(statuses)],
        })
    get_collection(ENQUIRIES).insert_many(enquiries)


def seed_test_drives(cars, customers, employees):
    active_cars = [c for c in cars if c["status"] != "Sold"]
    sales_execs = [e["employee_id"] for e in employees if e["role"] == "Sales Executive"]
    statuses = ["Completed", "Completed", "Scheduled", "Cancelled"]
    test_drives = []
    for i in range(8):
        car = active_cars[i % len(active_cars)]
        customer = customers[(i + 2) % len(customers)]
        date = (days_ago(30 - i * 3)).strftime("%Y-%m-%d")
        test_drives.append({
            "test_drive_id": f"TD{i + 1:03d}",
            "customer_id": customer["customer_id"], "car_id": car["car_id"],
            "employee_id": sales_execs[i % len(sales_execs)],
            "date": date, "time": f"{10 + i % 6}:00",
            "status": statuses[i % len(statuses)],
            "remarks": "Customer satisfied with drive quality" if i % 2 == 0 else "",
            "created_at": days_ago(31 - i * 3),
        })
    get_collection(TEST_DRIVES).insert_many(test_drives)


def seed_sales(cars, customers, employees):
    sold_cars = [c for c in cars if c["status"] == "Sold"]
    sales_execs = [e["employee_id"] for e in employees if e["role"] == "Sales Executive"]
    sales = []
    for i, car in enumerate(sold_cars):
        customer = customers[i % len(customers)]
        selling_price = car["pricing"]["selling_price"]
        purchase_cost = car["pricing"]["purchase_price"]
        additional = car["pricing"]["repair_cost"] + car["pricing"]["other_expenses"]
        profit, margin = calculate_sale_profit(purchase_cost, additional, selling_price)
        sales.append({
            "sale_id": f"SALE{i + 1:03d}",
            "car_id": car["car_id"], "customer_id": customer["customer_id"],
            "employee_id": sales_execs[i % len(sales_execs)],
            "sale_date": days_ago(20 - i * 2),
            "purchase_cost": purchase_cost, "additional_expenses": additional,
            "selling_price": selling_price, "profit": profit, "profit_margin": margin,
            "payment_status": "Pending",
        })
    get_collection(SALES).insert_many(sales)
    return sales


def seed_payments(sales):
    payments = []
    payment_methods = ["Cash", "UPI", "Bank Transfer", "Card", "Finance"]
    counter = 1
    for i, sale in enumerate(sales):
        total = sale["selling_price"]
        if i % 3 == 0:
            # Fully paid in a single transaction
            payments.append({
                "payment_id": f"PAY{counter:03d}", "sale_id": sale["sale_id"], "amount": total,
                "payment_date": sale["sale_date"] + timedelta(days=1),
                "payment_method": payment_methods[i % len(payment_methods)], "payment_status": "Full",
            })
            counter += 1
            get_collection(SALES).update_one({"sale_id": sale["sale_id"]}, {"$set": {"payment_status": "Paid"}})
        else:
            # Split into an advance + balance payment
            advance = round(total * 0.4, 2)
            balance = round(total - advance, 2)
            payments.append({
                "payment_id": f"PAY{counter:03d}", "sale_id": sale["sale_id"], "amount": advance,
                "payment_date": sale["sale_date"] + timedelta(days=1),
                "payment_method": payment_methods[i % len(payment_methods)], "payment_status": "Partial",
            })
            counter += 1
            if counter <= 10 and i % 3 != 2:
                payments.append({
                    "payment_id": f"PAY{counter:03d}", "sale_id": sale["sale_id"], "amount": balance,
                    "payment_date": sale["sale_date"] + timedelta(days=5),
                    "payment_method": payment_methods[(i + 1) % len(payment_methods)], "payment_status": "Full",
                })
                counter += 1
                get_collection(SALES).update_one({"sale_id": sale["sale_id"]}, {"$set": {"payment_status": "Paid"}})
            else:
                get_collection(SALES).update_one({"sale_id": sale["sale_id"]}, {"$set": {"payment_status": "Partial"}})
        if counter > 10:
            break
    get_collection(PAYMENTS).insert_many(payments[:10])


def seed_ownership_transfers(sales, cars, sellers, customers):
    car_by_id = {c["car_id"]: c for c in cars}
    seller_by_id = {s["seller_id"]: s for s in sellers}
    customer_by_id = {c["customer_id"]: c for c in customers}
    statuses = ["Completed", "Processing", "Pending"]
    transfers = []
    for i, sale in enumerate(sales[:5]):
        car = car_by_id[sale["car_id"]]
        seller = seller_by_id.get(car["seller_id"])
        customer = customer_by_id.get(sale["customer_id"])
        transfers.append({
            "transfer_id": f"TRF{i + 1:03d}",
            "sale_id": sale["sale_id"],
            "previous_owner": seller["name"] if seller else "Dealership",
            "new_owner": customer["name"] if customer else "Unknown",
            "transfer_date": sale["sale_date"] + timedelta(days=7),
            "status": statuses[i % len(statuses)],
            "remarks": "RC transfer initiated via RTO" if i % 2 == 0 else "",
        })
    get_collection(OWNERSHIP_TRANSFERS).insert_many(transfers)


def main():
    print("Resetting collections...")
    reset_collections()

    print("Seeding sellers, employees, customers...")
    sellers = seed_sellers()
    employees = seed_employees()
    customers = seed_customers()

    print("Seeding cars...")
    cars = seed_cars(sellers)

    print("Seeding inspections, enquiries, test drives...")
    seed_inspections(cars, employees)
    seed_enquiries(cars, customers)
    seed_test_drives(cars, customers, employees)

    print("Seeding sales, payments, ownership transfers...")
    sales = seed_sales(cars, customers, employees)
    seed_payments(sales)
    seed_ownership_transfers(sales, cars, sellers, customers)

    print("Creating indexes...")
    create_indexes()

    print("Done. Sample data inserted successfully.")


if __name__ == "__main__":
    main()
