# AutoTrade – Used Car Sales & Dealership Management System

A full-stack DBMS mini-project that models the complete lifecycle of a used
car: acquisition from a seller → inspection → rule-based valuation →
inventory → customer enquiry → test drive → sale → payment → ownership
transfer.

## 1. Description

AutoTrade is a dealership management system for a used-car business. It
replaces spreadsheets and paper registers with a single application that
tracks every vehicle from the moment it is bought from a seller to the
moment it is resold to a customer, along with the money and paperwork that
moves alongside it.

## 2. Objectives

- Apply MongoDB document modelling (embedding vs. referencing) to a
  realistic multi-entity business process.
- Demonstrate CRUD, query operators, aggregation pipelines and indexing on
  a non-trivial dataset.
- Build a working rule-based decision system (car valuation) without
  machine learning, so every number on screen can be explained.
- Enforce real business rules (a sold car cannot be sold again, a payment
  cannot exceed the balance, etc.) at the API layer.

## 3. Features

- Dashboard with live statistics computed from MongoDB (never hardcoded).
- Car inventory: add / search / filter / update / delete / change status.
- Seller, customer and employee management.
- Vehicle inspection records with an auto-calculated overall score.
- Rule-based used-car valuation engine with a visible, step-by-step
  breakdown.
- Customer enquiries and test-drive scheduling, both blocked for sold cars.
- Sales workflow that atomically flips a car's status to `Sold`.
- Payment tracking that never allows overpayment, with partial/full status.
- Ownership transfer records tied to a completed sale.
- Analytics page with brand, fuel-type, monthly and profit-margin
  breakdowns, all driven by aggregation pipelines.

## 4. Technology Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript (Roboto font) |
| Backend    | Python 3, Flask                     |
| Database   | MongoDB (via PyMongo)               |
| Tooling    | MongoDB Compass for inspecting data  |

No frontend framework is used, so every DOM update in `static/js/*.js` is
plain `fetch` + template strings — easy to read and explain line by line.

## 5. System Architecture

```
Browser (HTML/CSS/JS)
     │  fetch() → JSON
     ▼
Flask app (app.py)
     │  Blueprints per module
     ▼
routes/*.py  ──uses──▶ services/valuation.py, services/profit.py
     │
     ▼
database/mongodb.py (PyMongo connection, ID generator, indexes)
     │
     ▼
MongoDB (10 collections)
```

Each route module is a Flask **Blueprint** that owns both the page route
(returns a template) and the `/api/...` JSON routes for that module. This
keeps every feature's server-side code in one file.

## 6. Folder Structure

```
autotrade/
├── app.py                  # creates the Flask app, registers blueprints
├── config.py                # reads MONGO_URI etc. from environment
├── requirements.txt
├── seed_data.py              # inserts sample data (run once)
├── .env.example
├── database/
│   └── mongodb.py            # connection, collection constants, generate_id, create_indexes
├── services/
│   ├── valuation.py           # rule-based market valuation
│   └── profit.py               # sale profit/margin calculation
├── routes/                    # one Blueprint per module (pages + API)
│   ├── cars.py, sellers.py, customers.py, inspections.py,
│   ├── enquiries.py, test_drives.py, sales.py, payments.py,
│   ├── ownership_transfers.py, employees.py, analytics.py, utils.py
├── templates/                 # Jinja2 HTML, one file per page + base.html
└── static/
    ├── css/style.css
    └── js/                     # one script per page + common.js
```

## 7. MongoDB Database Design

### Collections

| Collection            | Purpose |
|------------------------|---------|
| `cars`                 | Vehicle inventory, with pricing and condition **embedded** |
| `sellers`              | People/companies who sold cars to the dealership |
| `customers`            | People buying cars |
| `inspections`          | One document per inspection event, **referencing** `car_id` |
| `enquiries`            | Customer interest in a specific car |
| `testDrives`           | Scheduled/completed/cancelled test drives |
| `sales`                | The transaction that moves a car from Available to Sold |
| `payments`             | One or more payments against a `sale_id` |
| `ownershipTransfers`   | RC/ownership transfer tied to a `sale_id` |
| `employees`            | Staff who inspect, sell or manage |

### Why embedding for `cars`, referencing for the rest?

`pricing` and `condition` are **embedded** inside each car document because
they are always read and written together with the car — there is no case
where you'd want a car's price without its car. This avoids a `$lookup` on
the single most-read collection in the app.

`seller_id`, `customer_id`, `employee_id`, `car_id` and `sale_id` are kept
as **references** (plain string IDs, not MongoDB `$ref`) because sellers,
customers and employees are independent entities that are reused across
many documents (a seller can list many cars; a customer can have many
enquiries, test drives and sales). Embedding them would duplicate data and
make updates (e.g. a customer's phone number changing) inconsistent across
collections.

### Example document — `cars`

```json
{
  "car_id": "CAR006",
  "brand": "Tata", "model": "Nexon", "variant": "XZ+",
  "manufacturing_year": 2020, "fuel_type": "Diesel", "transmission": "Manual",
  "mileage": 38000, "color": "White", "registration_year": 2020,
  "previous_owners": 1, "seller_id": "SEL001",
  "pricing": {
    "purchase_price": 780000, "repair_cost": 10000, "other_expenses": 4000,
    "selling_price": 812000, "estimated_market_value": 752000, "expected_profit": 18000
  },
  "condition": {
    "engine_condition": 8, "body_condition": 7, "tyre_condition": 7, "interior_condition": 8,
    "accident_history": false, "service_history": true,
    "overall_condition": "Good", "inspection_score": 7.5
  },
  "status": "Sold",
  "created_at": "2026-06-20T10:00:00Z"
}
```

## 8. MongoDB Queries Used (viva reference)

```javascript
// Search cars by brand or model (case-insensitive)
db.cars.find({ $or: [
  { brand: { $regex: "hyundai", $options: "i" } },
  { model: { $regex: "hyundai", $options: "i" } }
]})

// Cars priced between two values, available only
db.cars.find({
  "pricing.selling_price": { $gte: 400000, $lte: 900000 },
  status: "Available"
})

// Cars with more than one previous owner and an accident history
db.cars.find({
  previous_owners: { $gt: 1 },
  "condition.accident_history": true
})

// All Petrol or Diesel automatic cars
db.cars.find({
  fuel_type: { $in: ["Petrol", "Diesel"] },
  transmission: "Automatic"
})

// Update a car's status after inspection
db.cars.updateOne({ car_id: "CAR014" }, { $set: { status: "Available" } })

// Delete a customer only if they have no sales (enforced in app code first)
db.customers.deleteOne({ customer_id: "CUS008" })
```

## 9. Aggregation Pipelines Used

```javascript
// Total revenue and profit across all sales
db.sales.aggregate([
  { $group: {
      _id: null,
      total_revenue: { $sum: "$selling_price" },
      total_profit: { $sum: "$profit" },
      total_sales: { $sum: 1 }
  }}
])

// Sales and revenue grouped by brand (joins sales -> cars)
db.sales.aggregate([
  { $lookup: { from: "cars", localField: "car_id", foreignField: "car_id", as: "car" } },
  { $unwind: "$car" },
  { $group: {
      _id: "$car.brand",
      units_sold: { $sum: 1 },
      revenue: { $sum: "$selling_price" },
      profit: { $sum: "$profit" }
  }},
  { $sort: { units_sold: -1 } }
])

// Monthly sales trend
db.sales.aggregate([
  { $group: {
      _id: { $dateToString: { format: "%Y-%m", date: "$sale_date" } },
      sales_count: { $sum: 1 },
      revenue: { $sum: "$selling_price" }
  }},
  { $sort: { _id: 1 } }
])

// Most popular fuel type across inventory
db.cars.aggregate([
  { $group: { _id: "$fuel_type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

## 10. Indexes

| Index | Reason |
|-------|--------|
| `cars.brand`, `cars.model` | Used on every search/filter call |
| `cars.pricing.selling_price` | Range queries for price filters |
| `cars.status` | Every "Available cars only" dropdown filters on this |
| `cars.car_id` (unique) | Primary lookup key, must stay unique |
| `customers.phone` | Customer search by phone |
| `customers.customer_id`, `sellers.seller_id`, `sales.sale_id`, `employees.employee_id` (unique) | Enforce uniqueness of business IDs |
| `sales.sale_date` | Analytics sort/filter by date |
| `sales.car_id` | Used to check "does this car already have a sale" |
| `enquiries.car_id`, `testDrives.car_id`, `payments.sale_id` | Fast per-car / per-sale lookups |

Indexes are created once at startup by `database/mongodb.py::create_indexes()`.

## 11. Installation

```bash
git clone <this-repo> autotrade
cd autotrade

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# edit .env if your MongoDB isn't on localhost:27017

python seed_data.py     # inserts sample data (safe to re-run — it resets first)
python app.py
```

Open **http://localhost:5000** in a browser.

## 12. Sample Login Credentials

No authentication is implemented in this version (the project focuses on
the data model and business rules). Adding a login screen and a role check
on the `employees` collection is listed under Future Enhancements.

## 13. Why MongoDB?

- **Natural fit for a car document**: a car has nested groups of fields
  (pricing, condition) that are always read together — a document model
  avoids joining three or four tables just to show one car card.
- **Schema flexibility**: different car statuses realistically need
  slightly different optional fields (e.g. `Under Inspection` cars may not
  yet have a `selling_price`), which a relational schema would force into
  nullable columns everywhere.
- **Aggregation pipeline** replaces what would otherwise be several `GROUP
  BY`/`JOIN` SQL queries with one readable, chainable pipeline — useful for
  the dashboard and analytics page.
- **Horizontal growth**: a dealership chain could shard `cars` by
  showroom/region later without redesigning the schema.

A relational database is not a bad choice here either — the point of this
project is to demonstrate MongoDB's document model and aggregation
framework on a domain that has a mix of tightly-coupled fields (pricing,
condition) and independent, reused entities (customers, sellers).

## 14. Embedding vs Referencing — summary

| Data | Choice | Why |
|------|--------|-----|
| Car pricing & condition | Embedded in `cars` | Always read/written with the car; 1:1 relationship |
| Seller → Cars | Referenced (`seller_id`) | One seller can list many cars; seller info shouldn't be duplicated |
| Customer → Enquiries/Test Drives/Sales | Referenced (`customer_id`) | A customer is reused across many transaction documents |
| Sale → Payments | Referenced (`sale_id`) | A sale can have 1..n payments over time |
| Sale → Ownership Transfer | Referenced (`sale_id`) | 1:1 but modelled separately since it's a distinct process stage with its own status lifecycle |

## 15. How the Valuation Algorithm Works

Implemented in `services/valuation.py`, purely rule-based (no ML):

1. **Base price** = the dealership's purchase price for that car.
2. **Age adjustment**: −4% of base price per year since manufacture
   (depreciation).
3. **Mileage adjustment**: −1% of base price for every 10,000 km driven
   beyond a 40,000 km baseline.
4. **Previous owner adjustment**: −3% of base price for every owner beyond
   the first.
5. **Condition adjustment**: ±2% of base price per point the inspection
   score (out of 10) sits above/below a "fair" baseline of 7.
6. **Accident adjustment**: flat −8% if the car has an accident record.
7. **Service history adjustment**: +5% if fully serviced, −2% if records
   are incomplete.

All six adjustments are summed with the base price to get the
**Estimated Market Value** (floored at 30% of base price so it never goes
unrealistically low). The dealership then applies an 8% margin on top to
get the **Recommended Selling Price**. Expected profit is the recommended
selling price minus (purchase price + repair cost + other expenses).

Every adjustment is returned by the API and rendered as a labelled bar on
the car details and valuation pages, so each rupee figure on screen can be
traced back to a specific, explainable rule.

## 16. Possible Viva Questions & Answers

**Q: Why did you choose MongoDB over MySQL/Oracle for this project?**
A: See section 13 — the mixed embedding/referencing model and the
aggregation framework map naturally onto a car's nested pricing/condition
fields plus reused entities like customers and sellers.

**Q: How do you keep a car's status consistent when it's sold?**
A: `routes/sales.py::create_sale()` performs the status update
(`cars.update_one({car_id}, {$set: {status: "Sold", ...}})`) in the same
request that inserts the sale document, immediately after checking the car
isn't already sold. This is enforced server-side, not just in the UI.

**Q: What stops a payment from exceeding the sale amount?**
A: `routes/payments.py::add_payment()` sums all existing payments for that
`sale_id`, computes the remaining balance, and rejects the request with a
400 error if the new amount would exceed it — before it ever reaches
MongoDB.

**Q: How is the inspection score calculated?**
A: The average of engine, body, tyre, interior (and electrical, for a
formal inspection) condition scores out of 10, rounded to 2 decimal
places. See `_overall_score()` in `routes/inspections.py`.

**Q: Why use `$lookup` in the analytics pipeline?**
A: Sales documents only store `car_id`; to filter or group sales by brand,
fuel type or transmission, the pipeline joins each sale to its car
document with `$lookup` + `$unwind` before grouping.

**Q: How are IDs like `CAR014` generated, and why not just use MongoDB's
ObjectId?**
A: `database/mongodb.py::generate_id()` finds the highest existing numeric
suffix for that collection's prefix and adds one. Human-readable IDs are
easier to reference during a live demo/viva than a raw ObjectId.

**Q: What happens if someone tries to delete a car that has already been
sold?**
A: `routes/cars.py::delete_car()` checks the `sales` collection for a
matching `car_id` first and returns a 409 error if a sale exists,
preventing an orphaned sale record.

## 17. Future Enhancements

- Authentication and role-based access control using the `employees`
  collection (Admin / Manager / Sales Executive / Inspector).
- File uploads for car photos and inspection reports (GridFS).
- Email/SMS notifications for enquiry follow-ups and payment due dates.
- Exporting sales/analytics reports to PDF or Excel.
- Replacing the CSS bar charts with a proper charting library once the
  student is comfortable explaining the current, dependency-free version.
