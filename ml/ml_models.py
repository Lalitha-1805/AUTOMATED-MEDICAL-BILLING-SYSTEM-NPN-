"""
ML Models for Medical Billing Validation
Classification and Anomaly Detection - Improved Version
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')


class MedicalBillingMLModels:
    def __init__(self):
        self.lr_model = None
        self.rf_model = None
        self.gb_model = None  # Gradient Boosting for better performance
        self.iso_forest = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        
    def prepare_data(self, df):
        """Prepare data for ML models with enhanced feature engineering"""
        df_processed = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['gender', 'hospital_id']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col])
            else:
                df_processed[col] = self.label_encoders[col].transform(df_processed[col])
        
        # Create features
        self.feature_columns = ['age', 'treatment_cost', 'insurance_coverage_limit', 
                               'gender', 'hospital_id', 'cost_exceeds_coverage']
        
        X = df_processed[self.feature_columns].copy()
        
        # Add derived features with enhanced engineering
        X['cost_coverage_ratio'] = X['treatment_cost'] / (X['insurance_coverage_limit'] + 1)
        X['age_group'] = pd.cut(X['age'], bins=[0, 30, 50, 70, 100], labels=[0, 1, 2, 3]).astype(int)
        
        # Enhanced features for improved fraud detection
        X['cost_squared'] = X['treatment_cost'] ** 2  # Capture non-linear relationships
        X['coverage_utilization'] = (X['insurance_coverage_limit'] - X['treatment_cost']) / (X['insurance_coverage_limit'] + 1)
        X['age_cost_interaction'] = X['age'] * X['treatment_cost'] / 100000  # Normalized interaction
        X['cost_polynomial'] = X['treatment_cost'] / 1000  # Scaled polynomial feature
        
        y = df_processed['fraud_label']
        
        return X, y
    
    def train_models(self, df_train):
        """Train all ML models with optimized hyperparameters"""
        print("\n[ML] Training models...")
        
        X_train, y_train = self.prepare_data(df_train)
        
        # Normalize features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # 1. Logistic Regression (fine-tuned)
        print("  ├─ Training Logistic Regression...")
        self.lr_model = LogisticRegression(
            max_iter=2000,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced',
            C=0.5,
            solver='lbfgs',
            tol=1e-4
        )
        self.lr_model.fit(X_train_scaled, y_train)
        
        # 2. Random Forest (optimized)
        print("  ├─ Training Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train_scaled, y_train)
        
        # 3. Gradient Boosting (new addition)
        print("  ├─ Training Gradient Boosting...")
        self.gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42
        )
        self.gb_model.fit(X_train_scaled, y_train)
        
        # 4. Isolation Forest (fine-tuned)
        print("  └─ Training Isolation Forest...")
        self.iso_forest = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_jobs=-1,
            max_samples='auto'
        )
        self.iso_forest.fit(X_train_scaled)
        
        print("  ✓ Models trained successfully")
    
    def evaluate_models(self, df_test):
        """Evaluate models on test set"""
        print("\n[EVALUATION] Assessing model performance...")
        
        X_test, y_test = self.prepare_data(df_test)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        # Evaluate Logistic Regression
        lr_pred = self.lr_model.predict(X_test_scaled)
        lr_pred_proba = self.lr_model.predict_proba(X_test_scaled)[:, 1]
        
        results['Logistic Regression'] = {
            'accuracy': accuracy_score(y_test, lr_pred),
            'precision': precision_score(y_test, lr_pred, zero_division=0),
            'recall': recall_score(y_test, lr_pred, zero_division=0),
            'f1': f1_score(y_test, lr_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, lr_pred),
            'predictions': lr_pred,
            'probabilities': lr_pred_proba
        }
        
        # Evaluate Random Forest
        rf_pred = self.rf_model.predict(X_test_scaled)
        rf_pred_proba = self.rf_model.predict_proba(X_test_scaled)[:, 1]
        
        results['Random Forest'] = {
            'accuracy': accuracy_score(y_test, rf_pred),
            'precision': precision_score(y_test, rf_pred, zero_division=0),
            'recall': recall_score(y_test, rf_pred, zero_division=0),
            'f1': f1_score(y_test, rf_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, rf_pred),
            'predictions': rf_pred,
            'probabilities': rf_pred_proba
        }
        
        # Evaluate Gradient Boosting
        gb_pred = self.gb_model.predict(X_test_scaled)
        gb_pred_proba = self.gb_model.predict_proba(X_test_scaled)[:, 1]
        
        results['Gradient Boosting'] = {
            'accuracy': accuracy_score(y_test, gb_pred),
            'precision': precision_score(y_test, gb_pred, zero_division=0),
            'recall': recall_score(y_test, gb_pred, zero_division=0),
            'f1': f1_score(y_test, gb_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, gb_pred),
            'predictions': gb_pred,
            'probabilities': gb_pred_proba
        }
        
        # Evaluate Isolation Forest
        iso_pred = self.iso_forest.predict(X_test_scaled)
        iso_pred_binary = (iso_pred == -1).astype(int)
        
        results['Isolation Forest'] = {
            'accuracy': accuracy_score(y_test, iso_pred_binary),
            'precision': precision_score(y_test, iso_pred_binary, zero_division=0),
            'recall': recall_score(y_test, iso_pred_binary, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, iso_pred_binary),
            'predictions': iso_pred_binary,
            'probabilities': None
        }
        
        # Print results
        for model_name, metrics in results.items():
            print(f"\n  {model_name}:")
            print(f"    • Accuracy:  {metrics['accuracy']:.4f}")
            print(f"    • Precision: {metrics['precision']:.4f}")
            print(f"    • Recall:    {metrics['recall']:.4f}")
            print(f"    • F1 Score:  {metrics['f1']:.4f}")
        
        return results
    
    def predict(self, X):
        """Make predictions on new data with improved ensemble"""
        X_scaled = self.scaler.transform(X)
        
        # Ensemble prediction with improved weighting
        lr_pred_proba = self.lr_model.predict_proba(X_scaled)[:, 1]
        rf_pred_proba = self.rf_model.predict_proba(X_scaled)[:, 1]
        gb_pred_proba = self.gb_model.predict_proba(X_scaled)[:, 1]
        iso_pred = (self.iso_forest.predict(X_scaled) == -1).astype(int)
        
        # Weighted ensemble with Gradient Boosting emphasis
        ensemble_proba = (
            lr_pred_proba * 0.25 +
            rf_pred_proba * 0.3 +
            gb_pred_proba * 0.35 +
            iso_pred * 0.1
        )
        
        return {
            'lr_proba': lr_pred_proba,
            'rf_proba': rf_pred_proba,
            'gb_proba': gb_pred_proba,
            'iso_pred': iso_pred,
            'ensemble_proba': ensemble_proba,
            'ensemble_pred': (ensemble_proba > 0.5).astype(int)
        }
    
    def save_models(self, model_dir='models'):
        """Save trained models to disk"""
        os.makedirs(model_dir, exist_ok=True)
        
        with open(f'{model_dir}/logistic_regression.pkl', 'wb') as f:
            pickle.dump(self.lr_model, f)
        with open(f'{model_dir}/random_forest.pkl', 'wb') as f:
            pickle.dump(self.rf_model, f)
        with open(f'{model_dir}/gradient_boosting.pkl', 'wb') as f:
            pickle.dump(self.gb_model, f)
        with open(f'{model_dir}/isolation_forest.pkl', 'wb') as f:
            pickle.dump(self.iso_forest, f)
        with open(f'{model_dir}/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        with open(f'{model_dir}/label_encoders.pkl', 'wb') as f:
            pickle.dump(self.label_encoders, f)
        with open(f'{model_dir}/feature_columns.pkl', 'wb') as f:
            pickle.dump(self.feature_columns, f)
        
        print(f"\n✓ Models saved to {model_dir}/")
    
    def load_models(self, model_dir='models'):
        """Load pre-trained models from disk"""
        try:
            with open(f'{model_dir}/logistic_regression.pkl', 'rb') as f:
                self.lr_model = pickle.load(f)
            with open(f'{model_dir}/random_forest.pkl', 'rb') as f:
                self.rf_model = pickle.load(f)
            with open(f'{model_dir}/gradient_boosting.pkl', 'rb') as f:
                self.gb_model = pickle.load(f)
            with open(f'{model_dir}/isolation_forest.pkl', 'rb') as f:
                self.iso_forest = pickle.load(f)
            with open(f'{model_dir}/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            with open(f'{model_dir}/label_encoders.pkl', 'rb') as f:
                self.label_encoders = pickle.load(f)
            with open(f'{model_dir}/feature_columns.pkl', 'rb') as f:
                self.feature_columns = pickle.load(f)
            
            print(f"✓ Models loaded from {model_dir}/")
        except Exception as e:
            print(f"Error loading models: {e}")


def main():
    print("=" * 60)
    print("ML MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # Load dataset
    print("\n[1/4] Loading dataset...")
    df = pd.read_csv('data/medical_billing_dataset.csv')
    
    # Split data
    print("[2/4] Splitting data (80% train, 20% test)...")
    train_size = int(0.8 * len(df))
    df_train = df[:train_size]
    df_test = df[train_size:]
    print(f"  • Training: {len(df_train)} records")
    print(f"  • Testing: {len(df_test)} records")
    
    # Train models
    print("[3/4] Training models...")
    ml_system = MedicalBillingMLModels()
    ml_system.train_models(df_train)
    
    # Evaluate models
    print("[4/4] Evaluating models...")
    results = ml_system.evaluate_models(df_test)
    
    # Save models
    ml_system.save_models('models')
    
    print("\n" + "=" * 60)
    print("✓ ML TRAINING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()


def main():
    print("=" * 60)
    print("ML MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # Load dataset
    print("\n[1/4] Loading dataset...")
    df = pd.read_csv('data/medical_billing_dataset.csv')
    
    # Split data
    print("[2/4] Splitting data (80% train, 20% test)...")
    train_size = int(0.8 * len(df))
    df_train = df[:train_size]
    df_test = df[train_size:]
    print(f"  • Training: {len(df_train)} records")
    print(f"  • Testing: {len(df_test)} records")
    
    # Train models
    print("[3/4] Training models...")
    ml_system = MedicalBillingMLModels()
    ml_system.train_models(df_train)
    
    # Evaluate models
    print("[4/4] Evaluating models...")
    results = ml_system.evaluate_models(df_test)
    
    # Save models
    ml_system.save_models('models')
    
    print("\n" + "=" * 60)
    print("✓ ML TRAINING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
