# My Flask Web Project
This is a simple Flask web project that demonstrates how to set up a basic web application structure with routes, models, and services. It includes a sample route and a template rendering example.

# How to Run This Flask Project

## 1. Set Up the Environment
### Step 1: Create a Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate the Virtual Environment
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

## 2. Configure Environment Variables
```bash
SECRET_KEY=supersecretkey
```

## 3. Run project
```bash
python run.py
```
Then open your browser and navigate to:
```
http://127.0.0.1:5000/
```
# Project Structure
my_web_project/
├── app/
│   ├── routes/
│   ├── models/
│   ├── services/
│   ├── templates/
│   └── static/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md

