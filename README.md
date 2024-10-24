
# **Rule Engine Application**

This project is a **Rule Engine with AST** that allows users to create, manage, and evaluate rules based on user data. The system provides **metadata management** (name, description, status) and supports **user-defined functions** like `isSenior(age)`. Rules can be marked as **active or inactive** to manage which ones are used in evaluations.

---

## **Table of Contents**
1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Installation](#installation)
4. [Database Schema](#database-schema)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Examples](#examples)
8. [Project Structure](#project-structure)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

---

## **Features**
- Create rules with metadata (name, description, status).
- Mark rules as **active** or **inactive** for better management.
- Evaluate rules against user-provided data.
- Support for **user-defined functions** like `isSenior(age)`.
- Store rules and metadata in **MySQL database**.
- Use **Bootstrap-based frontend** for a responsive and modern UI.
- Error handling for invalid inputs or data formats.

---

## **Technology Stack**
- **Frontend:** HTML, CSS (Bootstrap), JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Styling:** Bootstrap 5

---

## **Installation**

### Prerequisites
- **Python 3.x**
- **MySQL Server**
- **pip** (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Install Dependencies
```bash
pip install Flask Flask-Cors mysql-connector-python
```

### Step 3: Configure MySQL
1. Create a database named `rule_engine`.
2. Use the following SQL query to create the `rules` table:

```sql
CREATE TABLE rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_string TEXT NOT NULL,
    ast JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive') DEFAULT 'active'
);
```

### Step 4: Run the Flask Application
```bash
python app.py
```

### Step 5: Access the Application
Open your browser and go to:
```
http://localhost:5000
```

---

## **Database Schema**
The **`rules` table** stores information about each rule along with its metadata:

| Column       | Type               | Description                               |
|--------------|--------------------|-------------------------------------------|
| `id`         | INT (Primary Key)  | Auto-incremented ID of the rule.          |
| `rule_name`  | VARCHAR(255)       | Name of the rule.                         |
| `description`| TEXT               | Description of the rule.                  |
| `rule_string`| TEXT               | The rule logic as a string.               |
| `ast`        | JSON               | Abstract Syntax Tree (AST) of the rule.   |
| `created_at` | TIMESTAMP          | Timestamp when the rule was created.      |
| `updated_at` | TIMESTAMP          | Timestamp when the rule was last updated. |
| `status`     | ENUM('active', 'inactive') | Active or inactive status of the rule.|

---

## **Usage**

1. **Create a Rule:**
   - Enter the **rule name, description, and rule logic** in the UI.
   - Select the **status** as "Active" or "Inactive".
   - Click **"Create Rule"**.

2. **Evaluate a Rule:**
   - Enter **user data in JSON format**.
   - Click **"Evaluate Rule"**.
   - The application will display whether the user is **"Eligible"** or **"Not Eligible"**.

3. **Activate/Deactivate Rules:**
   - Use the status dropdown when creating a rule.
   - Only **active rules** are evaluated.

---

## **API Endpoints**

### 1. **Create Rule**
**Endpoint:**  
`POST /api/create_rule`

**Request Body:**
```json
{
  "rule_name": "Sales Rule",
  "description": "Rule for sales employees",
  "rule_string": "(age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')",
  "status": "active"
}
```

**Response:**
```json
{
  "message": "Rule created successfully!",
  "ast": { ... }
}
```

### 2. **Evaluate Rule**
**Endpoint:**  
`POST /api/evaluate_rule`

**Request Body:**
```json
{
  "data": {
    "age": 35,
    "department": "Sales",
    "salary": 60000,
    "experience": 3
  }
}
```

**Response:**
```json
{
  "result": true
}
```

---

## **Examples**

### Example Rule 1:
- **Rule String:**  
  `(age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')`

- **User Data:**
  ```json
  {
    "age": 35,
    "department": "Sales",
    "salary": 60000,
    "experience": 3
  }
  ```

- **Expected Result:**  
  `True`

### Example Rule 2:
- **Rule String:**  
  `isSenior(age)`

- **User Data:**
  ```json
  {
    "age": 65,
    "department": "Management",
    "salary": 80000,
    "experience": 30
  }
  ```

- **Expected Result:**  
  `True`

---

## **Project Structure**

```
/your-project/
├── app.py                   # Flask backend
├── /static/                 # Static files (Bootstrap CSS/JS)
│   ├── css/
│   │   └── bootstrap.min.css
│   └── js/
│       └── bootstrap.bundle.min.js
├── /templates/              # HTML templates
│   └── index.html
└── requirements.txt         # Python dependencies
```

---

## **Troubleshooting**

1. **Issue:** `KeyError: '(' in parse_rule()`  
   **Solution:** Ensure parentheses are correctly balanced in the rule string.

2. **Issue:** `MySQL Error: Database not found`  
   **Solution:** Verify that MySQL is running and the **`rule_engine` database** is created.

3. **Issue:** `Invalid JSON Format`  
   **Solution:** Ensure that user data is entered in **valid JSON format** in the UI.

4. **Issue:** `No active rule found`  
   **Solution:** Make sure there is at least one **active rule** in the database.

---

## **Expected and Implemented Features Comparison**

| **Requirement**                            | **Implemented Feature**                                            | **Status**                  |
|--------------------------------------------|---------------------------------------------------------------------|-----------------------------|
| Simple UI, API, Backend, Data              | HTML/Bootstrap UI + Flask API + MySQL backend                      | ✔️ Implemented              |
| Determine eligibility based on attributes  | Evaluates user eligibility using rules and ASTs                    | ✔️ Implemented              |
| AST (Abstract Syntax Tree) representation  | Node class with left, right, value, and type fields                | ✔️ Implemented              |
| Dynamic rule creation and modification     | create_rule() API allows rule creation, update_status() allows status changes | ✔️ Implemented |
| Database choice for rule storage           | MySQL database used to store rules and metadata                    | ✔️ Implemented              |
| Sample Rules                               | Provided rules: (age > 30 AND department = 'Sales') OR ...         | ✔️ Implemented              |
| API Design: create_rule(rule_string)       | Takes a string and parses it into an AST                           | ✔️ Implemented              |
| API Design: combine_rules(rules)           | Combines multiple rules (future scope, basic version implemented)  | ⚠️ Basic implementation     |
| API Design: evaluate_rule(JSON data)       | Evaluates rules against user data JSON                             | ✔️ Implemented              |
| Test Cases: AST verification               | AST structure validated via create_rule() output                   | ✔️ Implemented              |
| Test Cases: Evaluation of JSON scenarios   | Sample data evaluated correctly against rules                      | ✔️ Implemented              |
| Error Handling                             | Validation for invalid rules, malformed JSON                       | ✔️ Implemented              |
| Validations for attributes catalog         | Ensured user data only uses catalog attributes                     | ✔️ Implemented              |
| Modification of rules                      | Status change and update API for rule modification                 | ✔️ Implemented              |
| Support for user-defined functions         | isSenior(age) function implemented                                 | ✔️ Implemented              |
