"""
Dynamic Approval Examples Data Module
Converts approval examples to structured data for dashboard integration
"""

# Approval Examples Data - Structured for Dynamic Dashboard
APPROVAL_EXAMPLES = [
    {
        "id": "CLM001-APR",
        "status": "APPROVED",
        "patient_name": "John Anderson",
        "patient_id": "PAT001",
        "diagnosis_code": "782.1",
        "diagnosis_name": "Rash and other non-specific skin eruption",
        "procedure_code": "99213",
        "procedure_name": "Established patient office visit - moderate",
        "treatment_cost": 2500.00,
        "approval_reason": "Standard outpatient procedure, all documentation complete",
        "fraud_risk_score": 0.08,
        "processing_time_days": 2.1,
        "insurance_coverage": 80,
        "insurance_amount": 2000.00,
        "patient_responsibility": 20,
        "patient_amount": 500.00,
    },
    {
        "id": "CLM002-APR",
        "status": "APPROVED",
        "patient_name": "Maria Garcia",
        "patient_id": "PAT002",
        "diagnosis_code": "786.50",
        "diagnosis_name": "Chest pain, unspecified",
        "procedure_code": "99285",
        "procedure_name": "Emergency department visit - high complexity",
        "treatment_cost": 1850.00,
        "approval_reason": "Emergency visit, medically necessary, all codes valid",
        "fraud_risk_score": 0.05,
        "processing_time_days": 1.8,
        "insurance_coverage": 90,
        "insurance_amount": 1665.00,
        "patient_responsibility": 10,
        "patient_amount": 185.00,
    },
    {
        "id": "CLM003-APR",
        "status": "APPROVED",
        "patient_name": "Robert Smith",
        "patient_id": "PAT003",
        "diagnosis_code": "Z12.11",
        "diagnosis_name": "Encounter for screening for malignant neoplasm of colon",
        "procedure_code": "45398",
        "procedure_name": "Colonoscopy with biopsy",
        "treatment_cost": 1200.00,
        "approval_reason": "Preventive care covered at 100%, routine screening",
        "fraud_risk_score": 0.03,
        "processing_time_days": 2.5,
        "insurance_coverage": 100,
        "insurance_amount": 1200.00,
        "patient_responsibility": 0,
        "patient_amount": 0.00,
    },
    {
        "id": "CLM004-APR",
        "status": "APPROVED",
        "patient_name": "Jennifer Lee",
        "patient_id": "PAT004",
        "diagnosis_code": "780.39",
        "diagnosis_name": "Fever, unspecified",
        "procedure_code": "70010",
        "procedure_name": "Hospital admission, routine",
        "treatment_cost": 8500.00,
        "approval_reason": "Medically necessary hospitalization, all procedures authorized",
        "fraud_risk_score": 0.12,
        "processing_time_days": 3.2,
        "insurance_coverage": 80,
        "insurance_amount": 6800.00,
        "patient_responsibility": 20,
        "patient_amount": 1700.00,
        "days_hospitalized": 3,
    },
    {
        "id": "CLM005-APR",
        "status": "APPROVED",
        "patient_name": "Michael Brown",
        "patient_id": "PAT005",
        "diagnosis_code": "K04.9",
        "diagnosis_name": "Unspecified disease of pulp and periapical tissues",
        "procedure_code": "31365",
        "procedure_name": "Root canal therapy",
        "treatment_cost": 950.00,
        "approval_reason": "Endodontic procedure covered under plan, tooth #14",
        "fraud_risk_score": 0.07,
        "processing_time_days": 2.0,
        "insurance_coverage": 50,
        "insurance_amount": 475.00,
        "patient_responsibility": 50,
        "patient_amount": 475.00,
    },
    {
        "id": "CLM006-APR",
        "status": "APPROVED",
        "patient_name": "Sarah Wilson",
        "patient_id": "PAT006",
        "diagnosis_code": "F32.9",
        "diagnosis_name": "Major depressive disorder, single episode",
        "procedure_code": "90834",
        "procedure_name": "Psychotherapy, 45 minutes",
        "treatment_cost": 250.00,
        "approval_reason": "Mental health coverage, licensed therapist, within benefit limits",
        "fraud_risk_score": 0.04,
        "processing_time_days": 1.5,
        "insurance_coverage": 85,
        "insurance_amount": 212.50,
        "patient_responsibility": 15,
        "patient_amount": 37.50,
        "session_count": 1,
    },
    {
        "id": "CLM007-APR",
        "status": "APPROVED",
        "patient_name": "David Martinez",
        "patient_id": "PAT007",
        "diagnosis_code": "M25.5",
        "diagnosis_name": "Pain in unspecified joint",
        "procedure_code": "97110",
        "procedure_name": "Physical therapy evaluation",
        "treatment_cost": 1300.00,
        "approval_reason": "Post-injury rehabilitation, medically necessary, licensed PT",
        "fraud_risk_score": 0.06,
        "processing_time_days": 2.3,
        "insurance_coverage": 80,
        "insurance_amount": 1040.00,
        "patient_responsibility": 20,
        "patient_amount": 260.00,
        "session_count": 12,
    },
    {
        "id": "CLM008-APR",
        "status": "APPROVED",
        "patient_name": "Emily Johnson",
        "patient_id": "PAT008",
        "diagnosis_code": "E11.9",
        "diagnosis_name": "Type 2 diabetes mellitus without complications",
        "procedure_code": "99214",
        "procedure_name": "Established patient office visit - moderate to high",
        "treatment_cost": 800.00,
        "approval_reason": "Chronic disease management, routine follow-up visit",
        "fraud_risk_score": 0.05,
        "processing_time_days": 1.9,
        "insurance_coverage": 80,
        "insurance_amount": 640.00,
        "patient_responsibility": 20,
        "patient_amount": 160.00,
    },
    {
        "id": "CLM009-APR",
        "status": "APPROVED",
        "patient_name": "Christopher Davis",
        "patient_id": "PAT009",
        "diagnosis_code": "I10",
        "diagnosis_name": "Essential (primary) hypertension",
        "procedure_code": "99212",
        "procedure_name": "Established patient office visit - low",
        "treatment_cost": 500.00,
        "approval_reason": "Hypertension management, routine visit, medication adjustment",
        "fraud_risk_score": 0.04,
        "processing_time_days": 1.6,
        "insurance_coverage": 80,
        "insurance_amount": 400.00,
        "patient_responsibility": 20,
        "patient_amount": 100.00,
    },
    {
        "id": "CLM010-APR",
        "status": "APPROVED",
        "patient_name": "Amanda Thompson",
        "patient_id": "PAT010",
        "diagnosis_code": "M79.3",
        "diagnosis_name": "Panniculitis, unspecified",
        "procedure_code": "20610",
        "procedure_name": "Therapeutic injection, major joint or bursa",
        "treatment_cost": 1150.00,
        "approval_reason": "Joint injection therapy, clinically indicated, orthopedic specialist",
        "fraud_risk_score": 0.08,
        "processing_time_days": 2.4,
        "insurance_coverage": 80,
        "insurance_amount": 920.00,
        "patient_responsibility": 20,
        "patient_amount": 230.00,
    },
]


def get_all_examples():
    """Get all approval examples"""
    return APPROVAL_EXAMPLES


def get_example_by_id(claim_id):
    """Get specific approval example by ID"""
    for example in APPROVAL_EXAMPLES:
        if example["id"] == claim_id:
            return example
    return None


def get_examples_summary():
    """Get summary statistics of all examples"""
    if not APPROVAL_EXAMPLES:
        return {}
    
    total_claims = len(APPROVAL_EXAMPLES)
    total_amount = sum(e["treatment_cost"] for e in APPROVAL_EXAMPLES)
    avg_processing_time = sum(e["processing_time_days"] for e in APPROVAL_EXAMPLES) / total_claims
    avg_fraud_risk = sum(e["fraud_risk_score"] for e in APPROVAL_EXAMPLES) / total_claims
    total_insurance_paid = sum(e["insurance_amount"] for e in APPROVAL_EXAMPLES)
    
    return {
        "total_claims": total_claims,
        "total_amount": total_amount,
        "avg_processing_time": avg_processing_time,
        "avg_fraud_risk": avg_fraud_risk,
        "total_insurance_paid": total_insurance_paid,
        "total_patient_responsibility": sum(e["patient_amount"] for e in APPROVAL_EXAMPLES),
    }


def filter_examples(status=None, fraud_risk_max=None, min_amount=None, max_amount=None):
    """Filter examples based on criteria"""
    results = APPROVAL_EXAMPLES.copy()
    
    if status:
        results = [e for e in results if e["status"] == status.upper()]
    
    if fraud_risk_max is not None:
        results = [e for e in results if e["fraud_risk_score"] <= fraud_risk_max]
    
    if min_amount is not None:
        results = [e for e in results if e["treatment_cost"] >= min_amount]
    
    if max_amount is not None:
        results = [e for e in results if e["treatment_cost"] <= max_amount]
    
    return results
