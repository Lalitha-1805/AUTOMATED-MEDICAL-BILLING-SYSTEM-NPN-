"""
Database Models for Medical Billing System
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    """User model with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='hospital_staff')  # hospital_staff, insurance_admin
    hospital_id = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Claim(db.Model):
    """Medical claim model"""
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.String(20), nullable=False, index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    diagnosis_code = db.Column(db.String(10), nullable=False)
    procedure_code = db.Column(db.String(10), nullable=False)
    treatment_cost = db.Column(db.Float, nullable=False)
    insurance_coverage_limit = db.Column(db.Float, nullable=False)
    claim_date = db.Column(db.Date, nullable=False, index=True)
    hospital_id = db.Column(db.String(20), nullable=False)
    
    # Validation results
    validation_status = db.Column(db.String(20), default='Pending')  # Approved, Rejected, Manual Review
    validation_reason = db.Column(db.Text)
    fraud_probability = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Validation details (JSON)
    validation_details = db.Column(db.Text)  # JSON string
    ml_predictions = db.Column(db.Text)  # JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Claim {self.claim_id}>'
    
    def get_validation_details(self):
        """Parse JSON validation details"""
        if self.validation_details:
            details = json.loads(self.validation_details)
            # If it's a dict with 'details' key (old format), return the list
            if isinstance(details, dict) and 'details' in details:
                return details['details']
            # If it's already a list, return it
            if isinstance(details, list):
                return details
            # If it's a dict (duplicate or other special case), convert to list format
            if isinstance(details, dict):
                # For duplicate checks and other special cases, create a synthetic list
                return [{
                    'rule': 'Validation Check',
                    'passed': details.get('duplicate_check', False),
                    'reason': 'Duplicate claim detected' if details.get('duplicate_check') else 'Validation check',
                    'severity': 'high' if details.get('duplicate_check') else 'info'
                }]
            # Otherwise return empty list
            return []
        return []
    
    def set_validation_details(self, details):
        """Set validation details as JSON"""
        self.validation_details = json.dumps(details)
    
    def get_ml_predictions(self):
        """Parse JSON ML predictions"""
        if self.ml_predictions:
            return json.loads(self.ml_predictions)
        return {}
    
    def set_ml_predictions(self, predictions):
        """Set ML predictions as JSON"""
        self.ml_predictions = json.dumps(predictions)


class BillUpload(db.Model):
    """Uploaded bill document model"""
    __tablename__ = 'bill_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), default='pdf')  # pdf, image
    extracted_text = db.Column(db.Text)
    claim_id = db.Column(db.String(20), db.ForeignKey('claims.claim_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BillUpload {self.filename}>'


class ValidationReport(db.Model):
    """Validation report model"""
    __tablename__ = 'validation_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total_claims = db.Column(db.Integer)
    approved_count = db.Column(db.Integer)
    rejected_count = db.Column(db.Integer)
    manual_review_count = db.Column(db.Integer)
    fraud_detection_rate = db.Column(db.Float)
    average_fraud_probability = db.Column(db.Float)
    
    # Model metrics
    model_accuracy = db.Column(db.Float)
    model_precision = db.Column(db.Float)
    model_recall = db.Column(db.Float)
    
    # Summary JSON
    summary = db.Column(db.Text)  # JSON with detailed stats
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class ClaimValidationReport(db.Model):
    """Per-claim validation report for the Claim Assistance Bot"""
    __tablename__ = 'claim_validation_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), unique=True, index=True)
    approval_status = db.Column(db.String(20), default='PENDING')  # APPROVED, REJECTED, PENDING
    violations = db.Column(db.Text)  # Comma-separated violation codes
    fraud_risk_score = db.Column(db.Float, default=0.0)  # 0-100
    anomaly_flags = db.Column(db.Text)  # Comma-separated anomaly types
    missing_documents = db.Column(db.Text)  # Comma-separated missing doc types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClaimValidationReport {self.claim_id}>'


class AnomalyLog(db.Model):
    """Log for detected anomalies"""
    __tablename__ = 'anomaly_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(20), db.ForeignKey('claims.claim_id'), index=True)
    anomaly_type = db.Column(db.String(50), nullable=False)  # duplicate, over-billing, invalid_mapping, etc.
    anomaly_score = db.Column(db.Float)
    details = db.Column(db.Text)  # JSON
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AnomalyLog {self.claim_id}>'
    
    def get_details(self):
        """Parse JSON details"""
        if self.details:
            return json.loads(self.details)
        return {}
    
    def set_details(self, details):
        """Set details as JSON"""
        self.details = json.dumps(details)


def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")
