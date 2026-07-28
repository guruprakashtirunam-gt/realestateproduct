# Indian Realty Hub — Backend

A Django REST Framework backend built to power the "Indian Realty Hub" frontend
(`realestatedocuments.html`). It replaces the hardcoded `listings`/`cities`
JS arrays with a real PostgreSQL-backed API, adds admin management, lead
capture, and a server-side EMI calculator.

## Stack
- Python 3.10+
- Django 5 + Django REST Framework
- PostgreSQL
- django-filter (search/filtering), django-cors-headers (CORS)

## 1. Setup

```bash
cd realty_backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure the database

Create a Postgres database and user:

```sql
CREATE DATABASE realty_hub;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE realty_hub TO postgres;
```

Copy `.env.example` to `.env` and fill in your own values (DB credentials,
a real `SECRET_KEY`, and the origin your frontend is served from):

```bash
cp .env.example .env
```

## 3. Migrate and seed demo data

```bash
python3 manage.py migrate
python3 manage.py seed_demo_data      # loads the same 8 cities / 8 listings from the frontend mockup
python3 manage.py createsuperuser     # admin account, used to manage listings
```

## 4. Run

```bash
python3 manage.py runserver
```

API is now live at `http://127.0.0.1:8000/api/`. Django admin is at
`http://127.0.0.1:8000/admin/`.

## 5. Point the frontend at it

The frontend currently reads from a hardcoded `listings`/`cities` JS array.
To wire it up to this API, replace those arrays with a `fetch()` call, e.g.:

```js
async function loadListings() {
  const res = await fetch('http://127.0.0.1:8000/api/properties/');
  const data = await res.json();
  return data.results; // paginated: {count, next, previous, results}
}
```

Make sure the frontend's origin (e.g. `http://127.0.0.1:5500` if using
VS Code Live Server) is listed in `CORS_ALLOWED_ORIGINS` in `.env`.

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/properties/` | Public | List/search/filter listings (paginated) |
| GET | `/api/properties/{id}/` | Public | Single listing detail |
| POST | `/api/properties/` | Admin | Create a listing |
| PUT/PATCH | `/api/properties/{id}/` | Admin | Update a listing |
| DELETE | `/api/properties/{id}/` | Admin | Remove a listing |
| GET | `/api/cities/` | Public | Cities with live listing counts |
| POST | `/api/newsletter/subscribe/` | Public | Email capture form |
| POST | `/api/inquiries/` | Public | "Contact me about this property" lead |
| POST | `/api/emi/calculate/` | Public | Server-side EMI calculation |
| POST | `/api/auth/token/` | Public | Exchange username/password for an auth token |

### Filtering `/api/properties/`

- `?city=Mumbai`
- `?status=sale` / `rent` / `new` (matches the All / For Sale / For Rent / New Launch buttons)
- `?property_type=Apartment`
- `?min_price=1000000&max_price=5000000`
- `?min_beds=2`
- `?search=bandra` (matches name, address, or city)
- `?ordering=price` / `-price` / `created_at` / `-created_at` / `area_sqft`

### Admin write access

Properties can only be created/edited/deleted by staff accounts. Get a token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -d "username=youradmin&password=yourpassword"
```

Then pass it on write requests:

```bash
curl -X POST http://127.0.0.1:8000/api/properties/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "city": 1, "address": "...", "price": 5000000, "area_sqft": 1200, ...}'
```

### EMI calculator example

```bash
curl -X POST http://127.0.0.1:8000/api/emi/calculate/ \
  -H "Content-Type: application/json" \
  -d '{"price": 8500000, "down_payment_percent": 20, "interest_rate": 8.5, "term_years": 20}'
```

Returns `monthly_emi`, `loan_amount`, `down_payment_amount`, `total_interest`,
`total_payable` — the same numbers the frontend's `calcEMI()` computes.

## Project layout

```
realty_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── realty_backend/        # project settings/urls
└── properties/            # the app: models, serializers, views, filters, admin
    └── management/commands/seed_demo_data.py
```

## Notes
- Rupee formatting (`₹4.20 Crore`, `₹32,000/mo`) is ported line-for-line from
  the frontend's `formatRupee`/`formatLakhCrore` JS so labels match exactly —
  see `properties/utils.py`.
- Listings are soft-deleted via `is_active` rather than hard-deleted by
  default in the public API (inactive listings are excluded from GET
  requests but preserved in the DB).
- This was tested end-to-end against a live server (migrations, seed data,
  filtering, search, EMI math, newsletter, inquiries, and admin-only write
  protection all verified working) before being handed to you.
