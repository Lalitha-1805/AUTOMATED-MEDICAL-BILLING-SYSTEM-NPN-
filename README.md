# Automated Medical Billing Validation System

## 🏥 Project Overview

A complete **AI/ML-powered web application** for automated medical billing validation and fraud detection. The system validates medical claims, detects fraudulent patterns, duplicate claims, and over-billing using machine learning models combined with rule-based healthcare compliance checks.

### Key Features

✅ **AI-Powered Validation**
- Logistic Regression model for claim classification
- Random Forest for sophisticated pattern detection
- Isolation Forest for anomaly detection
- Ensemble learning for robust predictions

✅ **Rule-Based Validation**
- Coverage limit compliance
- Diagnosis-procedure mapping validation
- Cost range verification
- Age-specific treatment rules
- Duplicate claim detection
- Cost-to-coverage ratio analysis

✅ **Web Application**
- Hospital staff dashboard for claim validation
- Insurance admin panel for system-wide analytics
- Role-based access control (Hospital Staff, Insurance Admin)
- Real-time fraud analytics and reporting

✅ **Dataset Generation**
- Automatically generates 100,000+ synthetic medical records
- Includes realistic fraud patterns:
  - Duplicate claims
  - Over-billing cases
  - Invalid diagnosis-procedure mappings
  - Cost exceeding coverage limits
- Saved as CSV and SQLite database

---

## 📊 Technology Stack

### Backend
- **Python 3.9+**
- **Flask 2.3+** - Web framework
- **SQLAlchemy** - ORM and database management
- **SQLite** - Database

### Machine Learning
- **Scikit-learn** - ML models
- **Pandas** - Data processing
- **NumPy** - Numerical computing
- **Matplotlib** - Visualization

### Frontend
- **HTML5, CSS3, JavaScript**
- **Bootstrap 5** - UI framework
- **Chart.js** - Interactive charts

### Additional
- **Flask-Session** - Session management
- **Werkzeug** - Security utilities
- **Pillow** - Image processing

---

## 🗂️ Project Structure

```
medical_billing_validation/
├── app/
│   ├── __init__.py              # Flask app, routes, API endpoints
│   ├── models.py                # Database models
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── bill_validation.html
│   │   ├── bill_validation_result.html
│   │   ├── admin_panel.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── ml/
│   ├── ml_models.py             # ML model training & inference
│   └── validation_rules.py       # Rule-based validation engine
├── data/
│   ├── medical_billing_dataset.csv  # Generated synthetic data
│   └── medical_billing.db           # SQLite database
├── models/
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── isolation_forest.pkl
│   ├── scaler.pkl
│   ├── label_encoders.pkl
│   └── feature_columns.pkl
├── uploads/                     # Directory for uploaded bills
├── generate_dataset.py          # Dataset generation script
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Windows/Linux/macOS

### Installation

#### 1. Clone/Download the Project
```bash
cd c:\Users\HP\Desktop\NPN\medical_billing_validation
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Generate Synthetic Dataset
```bash
python generate_dataset.py
```
This will:
- Generate 100,000 synthetic medical billing records
- Save to `data/medical_billing_dataset.csv`
- Create SQLite database at `data/medical_billing.db`
- Display statistics about fraud patterns

#### 5. Train Machine Learning Models
```bash
python ml/ml_models.py
```
This will:
- Load the generated dataset
- Split into 80% training, 20% testing
- Train Logistic Regression, Random Forest, and Isolation Forest
- Evaluate model performance (Accuracy, Precision, Recall)
- Save trained models to `models/` directory

#### 6. Run the Application
```bash
python run.py
```

The application will start at: **http://localhost:5000**

---

## 📋 How to Use

### For Hospital Staff

1. **Sign Up**
   - Go to http://localhost:5000/signup
   - Create account with:
     - Username
     - Email
     - Password
     - Role: Hospital Staff
     - Hospital ID (optional)

2. **Validate Claims**
   - Navigate to "Validate Bill"
   - Enter claim details:
     - Patient ID
     - Age, Gender
     - Diagnosis Code (ICD)
     - Procedure Code (CPT)
     - Treatment Cost
     - Insurance Coverage Limit
     - Hospital ID
   - Click "Validate Claim"
   - View detailed validation result with:
     - Approval/Rejection status
     - Fraud probability
     - Validation rules applied
     - ML model scores

3. **View Dashboard**
   - See all your validated claims
   - View statistics (Approved, Rejected, Manual Review)
   - Track claim status over time

### For Insurance Admins

1. **Sign Up as Admin**
   - Role: Insurance Admin
   - Get access to system-wide analytics

2. **Admin Panel**
   - View all claims across hospitals
   - Monitor fraud detection rate
   - See approval/rejection breakdown
   - View 30-day fraud trends
   - Analyze cost anomalies
   - Export reports

---

## 🧠 Machine Learning Models

### 1. Logistic Regression
- **Purpose**: Binary classification (Valid/Invalid claims)
- **Performance**: ~85% accuracy
- **Use Case**: Baseline model with interpretable results

### 2. Random Forest
- **Purpose**: Complex pattern detection
- **Performance**: ~92% accuracy
- **Use Case**: Handle non-linear relationships

### 3. Isolation Forest
- **Purpose**: Anomaly detection
- **Contamination**: 20% (expected fraud rate)
- **Use Case**: Detect unusual billing patterns

### Ensemble Model
- Combines predictions from all three models
- Uses weighted averaging for final fraud probability
- Threshold-based decision:
  - `> 0.8`: Automatically Rejected
  - `0.6-0.8`: Manual Review
  - `< 0.6`: Approved (if rules pass)

---

## ✅ Validation Rules

### Rule 1: Coverage Limit
Treatment cost must NOT exceed insurance coverage limit

### Rule 2: Diagnosis-Procedure Mapping
Selected procedure must be valid for the diagnosis code

### Rule 3: Cost Range
Cost must fall within typical range for the procedure

### Rule 4: Age-Specific Validation
Procedures must be age-appropriate
- Diabetes diagnosis unusual for age < 5
- Invasive procedures flagged for age > 80

### Rule 5: Duplicate Detection
Same patient + procedure + date = potential duplicate

### Rule 6: Pattern Analysis
High cost-to-coverage ratio indicates suspicious activity

---

## 📊 Dataset Specification

### Generated Synthetic Dataset (100,000 records)

**Columns:**
- `claim_id`: Unique claim identifier
- `patient_id`: Patient identifier
- `age`: Patient age (18-95)
- `gender`: M or F
- `diagnosis_code`: ICD-10 code
- `procedure_code`: CPT code
- `treatment_cost`: Cost in dollars
- `insurance_coverage_limit`: Coverage amount
- `claim_date`: Date of claim
- `hospital_id`: Hospital identifier
- `claim_status`: Valid/Invalid/Fraud
- `fraud_pattern`: Type of fraud (if any)
- `fraud_label`: 1 if Invalid/Fraud, 0 if Valid

**Fraud Distribution:**
- Valid Claims: ~80%
- Over-billing: ~8%
- Invalid Mapping: ~2%
- Duplicate: ~2%
- Cost Exceeds Coverage: ~3%
- Age Mismatch: ~5%

---

## 🔐 Authentication

- **Session-based login** using Flask-Session
- **Password hashing** with Werkzeug
- **Role-based access control**:
  - Hospital Staff: Can upload and validate own claims
  - Insurance Admin: Can view all claims and analytics

---

## 📈 Model Performance Metrics

The system evaluates models on:
- **Accuracy**: Overall correctness
- **Precision**: True positive rate (fraud detected correctly)
- **Recall**: False negative rate (missed frauds)
- **Confusion Matrix**: TP, TN, FP, FN breakdown

### Expected Performance
- **Accuracy**: 85-92%
- **Precision**: 80-88%
- **Recall**: 75-85%
- **F1-Score**: 0.80-0.87

---

