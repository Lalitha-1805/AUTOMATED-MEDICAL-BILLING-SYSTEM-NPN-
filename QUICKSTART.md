# Quick Start Guide - Medical Billing Validation System

## 🚀 Start in 5 Minutes

### Option 1: Automated Setup (Windows)
```bash
cd c:\Users\HP\Desktop\NPN\medical_billing_validation
setup.bat
```

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Generate Dataset
```bash
python generate_dataset.py
```
Output:
- 100,000 synthetic medical records
- Saved to `data/medical_billing_dataset.csv`
- SQLite database at `data/medical_billing.db`

#### Step 4: Train ML Models
```bash
python ml/ml_models.py
```
Output:
- Trained models saved to `models/` directory
- Performance metrics displayed

#### Step 5: Run Application
```bash
python run.py
```

### Step 6: Access the Web Interface

Open your browser and go to:
**http://localhost:5000**

---

## 👤 Test Login Credentials

Since it's a fresh database, you need to create an account first.

### Create Test Accounts

**Hospital Staff:**
1. Go to http://localhost:5000/signup
2. Fill in:
   - Username: `staff1`
   - Email: `staff@hospital.com`
   - Password: `password123`
   - Role: Hospital Staff
   - Hospital ID: H0001
3. Click "Create Account"

**Insurance Admin:**
1. Go to http://localhost:5000/signup
2. Fill in:
   - Username: `admin1`
   - Email: `admin@insurance.com`
   - Password: `password123`
   - Role: Insurance Admin
3. Click "Create Account"

---

## 🧪 Testing Validation

### Test Claim Example 1 (Should Approve)
- Patient ID: P12345
- Age: 45
- Gender: M
- Diagnosis: E10 (Type 1 Diabetes)
- Procedure: 99213 (Office Visit)
- Cost: $200
- Coverage: $5000

### Test Claim Example 2 (Should Flag as Fraud)
- Patient ID: P54321
- Age: 50
- Gender: F
- Diagnosis: I10 (Hypertension)
- Procedure: 99215 (High Complexity Visit)
- Cost: $15000 ⚠️ (Over-billing!)
- Coverage: $5000

---

## 📊 View Analytics

1. **Hospital Staff Dashboard**
   - Shows your validated claims
   - Statistics (Approved, Rejected, Manual Review)
   - Recent claims list

2. **Admin Panel** (Insurance Admin only)
   - All claims across hospitals
   - Fraud rate: Shows percentage of claims flagged as fraud
   - Fraud Trend Chart: 30-day trend
   - Claims by Status: Pie chart breakdown
   - Searchable claims table

---

## 🔍 Understanding Results

When you validate a claim, you'll see:

**Claim Status:**
- ✅ **Approved**: Passed all rules and low fraud probability
- ❌ **Rejected**: Failed critical rules or high fraud probability
- ⚠️ **Manual Review**: Medium risk, needs human review

**Fraud Probability:**
- 0-30%: Low risk (GREEN)
- 30-70%: Medium risk (YELLOW)
- 70-100%: High risk (RED)

**Validation Details:**
- Rule 1: Coverage Limit ✓/✗
- Rule 2: Diagnosis-Procedure ✓/✗
- Rule 3: Cost Range ✓/✗
- Rule 4: Age Specific ✓/✗
- Rule 5: Duplicate Detection ✓/✗
- Rule 6: Pattern Analysis ✓/✗

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `generate_dataset.py` | Creates 100K synthetic records |
| `ml/ml_models.py` | Trains ML models |
| `ml/validation_rules.py` | Implements 6 validation rules |
| `app/__init__.py` | Flask app & API routes |
| `app/models.py` | Database models |
| `app/templates/` | HTML templates |
| `app/static/` | CSS & JavaScript |

---

## ⚙️ Configuration

### Change Port
Edit `run.py`:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Change Database
Edit `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path/to/db.db'
```

---

## 🐛 Common Issues

**"Module not found" error**
```bash
pip install -r requirements.txt
```

**"Port 5000 already in use"**
- Change port in `run.py` to 5001, 5002, etc.
- Or: `netstat -ano | findstr :5000` (Windows)

**"Models not found" error**
```bash
python ml/ml_models.py
```

**Database locked**
- Stop the app and delete `medical_billing.db`
- Run setup again

---

## 📊 Demo Workflow

1. **Sign up as Hospital Staff**
2. **Upload test claims**:
   - Valid claim (should approve)
   - Suspicious claim (should flag)
   - Over-billing claim (should reject)
3. **View dashboard** to see results
4. **Sign up as Insurance Admin**
5. **View analytics** to see fraud trends

---

## 🎯 What to Expect

**Dataset Generation** (1-2 minutes)
- Creates 100,000 realistic medical records
- Introduces 20% fraud patterns
- Saves to CSV and SQLite

**Model Training** (2-3 minutes)
- Trains 3 ML models
- Evaluates on test set
- Saves trained models
- Performance: ~85-92% accuracy

**Web Application**
- Loads in seconds
- Responds instantly to validations
- Real-time fraud probability
- Live analytics updates

---

## 📞 Need Help?

1. Check the full README.md
2. Review generated logs
3. Ensure Python 3.9+ installed
4. Check internet connection for any online components

---

**Status**: ✅ Ready to Run
**Last Updated**: January 2024
