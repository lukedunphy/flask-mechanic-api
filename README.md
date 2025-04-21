# Mechanic Database Management System

This project is a modern, modular RESTful API built with Flask’s application factory pattern and Blueprints. On startup it auto‑creates MySQL tables, and exposes clear JSON endpoints for creating, reading, updating, and deleting customers and mechanics, as well as creating and listing service tickets.

- **Flask (3.1)** for the core web framework  
- **Flask‑SQLAlchemy** ORM to model complex relational data—supporting one‑to‑many and many‑to‑many associations with cascade deletes  
- **Marshmallow** (via Flask‑Marshmallow) for input validation and JSON serialization  
- **python‑dotenv** for secure, environment‑based configuration of credentials  
- Automatic table creation and a clear separation of concerns (config, extensions, models, schemas, routes)


## Tech Stack
- **Python**: 3.12.4  
- **Flask**  
- **Flask-SQLAlchemy**  
- **Flask-Marshmallow**  
- **Marshmallow-SQLAlchemy**  
- **MySQL** (Workbench)  
- **python-dotenv**  
- **Postman** (for testing)

## Requirements
- Python >= 3.12.4  
- MySQL server & MySQL Workbench  
- A MySQL database named `mechanic_db` (or update `DB_NAME` in config)

Install dependencies:  
```bash
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the project root and add:
```
DB_PASSWORD=your_mysql_password
```
(Optional defaults—do not need to set unless you change them)
```
DB_USER=root
DB_HOST=localhost
DB_NAME=mechanic_db
```

## Setup & Run
1. Ensure MySQL is running and the `mechanic_db` database exists.  
2. Populate `.env` with your MySQL password.  
3. Start the app:
   ```bash
   python app.py
   ```
   This will:
   - Auto-create tables via `db.create_all()`
   - Start the server at `http://127.0.0.1:5000`

## API Endpoints

### Customers (`/customers`)
- **Create Customer**  
  `POST /customers`  
  **Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890"
  }
  ```
  **Response (201)**:
  ```json
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890"
  }
  ```

- **Get All Customers**  
  `GET /customers`  
  **Response (200)**:
  ```json
  [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "123-456-7890"
    }
  ]
  ```

- **Update Customer**  
  `POST /customers/<customer_id>`  
  **Body**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "987-654-3210"
  }
  ```
  **Response (200)**:
  ```json
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "987-654-3210"
  }
  ```

- **Delete Customer**  
  `DELETE /customers/<customer_id>`  
  **Response (200)**:
  ```json
  { "message": "successfully deleted customer <customer_id>" }
  ```

---

### Mechanics (`/mechanics`)
- **Create Mechanic**  
  `POST /mechanics`  
  **Body**:
  ```json
  {
    "name": "Scottie",
    "email": "scottie@gmail.com",
    "phone": "678-463-2743",
    "salary": 1000000
  }
  ```
  **Response (201)**:
  ```json
  {
    "id": 4,
    "name": "Scottie",
    "email": "scottie@gmail.com",
    "phone": "678-463-2743",
    "salary": 1000000
  }
  ```

- **Get All Mechanics**  
  `GET /mechanics`  
  **Response (200)**:
  ```json
  [
    {
      "id": 2,
      "name": "Scottie",
      "email": "scottie@gmail.com",
      "phone": "678-463-2745",
      "salary": 100000
    },
    {
      "id": 4,
      "name": "Scottie",
      "email": "scottie@gmail.com",
      "phone": "678-463-2743",
      "salary": 100000
    }
  ]
  ```

- **Update Mechanic**  
  `PUT /mechanics/<mechanic_id>`  
  **Body**: same as Create  
  **Response (200)**:
  ```json
  {
    "id": 4,
    "name": "Scottie",
    "email": "scottie@gmail.com",
    "phone": "678-463-2743",
    "salary": 100000
  }
  ```

- **Delete Mechanic**  
  `DELETE /mechanics/<mechanic_id>`  
  **Response (200)**:
  ```json
  { "message": "successfully deleted mechanic <mechanic_id>" }
  ```

---

### Service Tickets (`/service-tickets`)
- **Create Service Ticket**  
  `POST /service-tickets`  
  **Body**:
  ```json
  {
    "VIN": "xvhnr8723",
    "service_date": "2025-10-15",
    "service_desc": "replaced brakes",
    "mechanic_ids": [2, 4],
    "customer_id": 4
  }
  ```
  **Response (200)**:
  ```json
  {
    "VIN": "xvhnr8723",
    "customer_id": 4,
    "service_date": "2025-10-15",
    "service_desc": "replaced brakes"
  }
  ```

- **Get All Service Tickets**  
  `GET /service-tickets`  
  **Response (200)**:
  ```json
  [
    {
      "VIN": "xvhnr8723",
      "customer_id": 2,
      "service_date": "2025-10-15",
      "service_desc": "replaced brakes"
    }
  ]
  ```

---

## Error Handling
- **400 Bad Request**: validation errors  
- **404 Not Found**: invalid resource IDs  
  ```json
  { "message": "invalid <resource> id" }
  ```
