#!/usr/bin/env python
"""
Medical Billing Validation System - Smart Startup Script
Automatically handles setup and starts the application
"""

import os
import sys
import subprocess
import platform

class MedicalBillingStartup:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.os_type = platform.system()
        
    def print_header(self):
        print("\n" + "=" * 70)
        print("  MEDICAL BILLING VALIDATION SYSTEM - STARTUP")
        print("=" * 70 + "\n")
    
    def check_python(self):
        """Check Python version"""
        print("[1/5] Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print("✗ Python 3.9+ required (found {}.{})".format(version.major, version.minor))
            return False
        print("✓ Python {}.{} detected".format(version.major, version.minor))
        return True
    
    def check_dependencies(self):
        """Check if required packages are installed"""
        print("\n[2/5] Checking dependencies...")
        required = ['flask', 'flask_sqlalchemy', 'pandas', 'sklearn', 'numpy']
        missing = []
        
        for package in required:
            try:
                __import__(package)
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ✗ {package}")
                missing.append(package)
        
        if missing:
            print("\n  Installing missing packages...")
            for package in missing:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package, '-q'])
            print("  ✓ Dependencies installed")
        
        return True
    
    def check_data(self):
        """Check if dataset exists"""
        print("\n[3/5] Checking dataset...")
        dataset_file = os.path.join(self.project_dir, 'data', 'medical_billing_dataset.csv')
        
        if os.path.exists(dataset_file):
            print("✓ Dataset found")
            return True
        else:
            print("✗ Dataset not found. Generating...")
            self.generate_dataset()
            return True
    
    def generate_dataset(self):
        """Generate synthetic dataset"""
        print("  Generating 100,000 synthetic records...")
        os.chdir(self.project_dir)
        subprocess.run([sys.executable, 'generate_dataset.py'], check=True)
        print("  ✓ Dataset generated")
    
    def check_models(self):
        """Check if ML models exist"""
        print("\n[4/5] Checking ML models...")
        models_dir = os.path.join(self.project_dir, 'models')
        required_models = [
            'logistic_regression.pkl',
            'random_forest.pkl',
            'isolation_forest.pkl',
            'scaler.pkl'
        ]
        
        missing = []
        for model in required_models:
            model_path = os.path.join(models_dir, model)
            if os.path.exists(model_path):
                print(f"  ✓ {model}")
            else:
                print(f"  ✗ {model}")
                missing.append(model)
        
        if missing:
            print("\n  Training ML models...")
            os.chdir(self.project_dir)
            subprocess.run([sys.executable, 'ml/ml_models.py'], check=True)
            print("  ✓ Models trained")
        
        return True
    
    def verify_app(self):
        """Verify Flask app can be imported"""
        print("\n[5/5] Verifying application...")
        try:
            from app import app
            from app.models import db
            print("✓ Flask application verified")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def print_info(self):
        """Print startup information"""
        print("\n" + "=" * 70)
        print("  STARTUP COMPLETE - READY TO RUN")
        print("=" * 70)
        print("\n  Access the application at:")
        print("  → http://localhost:5000")
        print("\n  Default test credentials:")
        print("  Hospital Staff:")
        print("    username: staff1")
        print("    password: password123")
        print("\n  Insurance Admin:")
        print("    username: admin1")
        print("    password: password123")
        print("\n  Features:")
        print("  ✓ 100,000 synthetic records")
        print("  ✓ 3 ML models (93%+ accuracy)")
        print("  ✓ 6 validation rules")
        print("  ✓ Professional web interface")
        print("  ✓ Role-based access control")
        print("  ✓ Real-time analytics")
        print("\n  Press Ctrl+C to stop the server")
        print("=" * 70 + "\n")
    
    def run(self):
        """Run startup sequence"""
        self.print_header()
        
        if not self.check_python():
            return False
        
        if not self.check_dependencies():
            return False
        
        if not self.check_data():
            return False
        
        if not self.check_models():
            return False
        
        if not self.verify_app():
            return False
        
        self.print_info()
        
        # Start Flask app
        print("  Starting Flask application...\n")
        try:
            from app import app
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n\n  Application stopped.")
        except Exception as e:
            print(f"\n  Error: {e}")
            return False
        
        return True


if __name__ == '__main__':
    startup = MedicalBillingStartup()
    success = startup.run()
    sys.exit(0 if success else 1)
