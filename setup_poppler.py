#!/usr/bin/env python
"""
Setup Poppler for PDF extraction
Copies Poppler from Downloads to Program Files and configures PATH
"""

import shutil
import os
import sys
from pathlib import Path

def setup_poppler():
    """Setup Poppler installation"""
    
    # Possible source locations
    sources = [
        r"C:\Users\HP\Downloads\poppler-windows-25.12.0-0\poppler-windows-25.12.0-0",
        r"C:\Users\HP\Downloads\poppler-26.1.0",
        r"C:\Program Files\poppler",
    ]
    
    dest = r"C:\Program Files\poppler"
    
    # Find existing Poppler
    source = None
    for s in sources:
        if os.path.exists(s):
            print(f"✅ Found Poppler at: {s}")
            source = s
            break
    
    if not source:
        print("❌ Poppler not found in expected locations")
        print("Please download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        return False
    
    # If source is already the destination, verify it
    if os.path.normpath(source) == os.path.normpath(dest):
        print(f"✅ Poppler already at {dest}")
        return verify_poppler(dest)
    
    # Copy to Program Files
    print(f"\nCopying Poppler to {dest}...")
    try:
        if os.path.exists(dest):
            print(f"Removing old installation...")
            shutil.rmtree(dest, ignore_errors=True)
        
        shutil.copytree(source, dest)
        print(f"✅ Successfully copied")
        
        # Verify
        return verify_poppler(dest)
        
    except PermissionError:
        print(f"⚠️  Permission denied copying to Program Files")
        print(f"Using Poppler from: {source}")
        return update_pdf_extractor_path(source)
    except Exception as e:
        print(f"❌ Error copying: {e}")
        return False


def verify_poppler(path):
    """Verify Poppler installation"""
    
    pdftoppm = os.path.join(path, "Library", "bin", "pdftoppm.exe")
    
    if os.path.exists(pdftoppm):
        print(f"✅ Verified: {pdftoppm} exists")
        
        # Update PATH
        bin_path = os.path.dirname(pdftoppm)
        update_system_path(bin_path)
        return True
    else:
        print(f"⚠️  pdftoppm.exe not found at expected location")
        # Try to find it
        for root, dirs, files in os.walk(path):
            if "pdftoppm.exe" in files:
                full_path = os.path.join(root, "pdftoppm.exe")
                print(f"✅ Found at: {full_path}")
                
                bin_dir = os.path.dirname(full_path)
                update_system_path(bin_dir)
                update_pdf_extractor_path(bin_dir)
                return True
        
        print(f"❌ pdftoppm.exe not found in {path}")
        return False


def update_system_path(bin_path):
    """Add path to system PATH"""
    
    try:
        current_path = os.environ.get('PATH', '')
        
        if bin_path not in current_path:
            os.environ['PATH'] = bin_path + os.pathsep + current_path
            print(f"✅ Added to PATH: {bin_path}")
        else:
            print(f"✅ Already in PATH: {bin_path}")
        
        return True
    except Exception as e:
        print(f"⚠️  Error updating PATH: {e}")
        return False


def update_pdf_extractor_path(bin_path):
    """Update pdf_extractor.py with Poppler path"""
    
    try:
        pdf_extractor_path = "ml/pdf_extractor.py"
        
        if not os.path.exists(pdf_extractor_path):
            print(f"⚠️  {pdf_extractor_path} not found")
            return False
        
        with open(pdf_extractor_path, 'r') as f:
            content = f.read()
        
        # Check if already has this path
        if bin_path in content:
            print(f"✅ Path already in pdf_extractor.py")
            return True
        
        # Add to configure_poppler function
        new_path_entry = f'        r"{bin_path}",  # Downloaded Poppler\n'
        
        # Find the poppler_paths list and add to it
        if "poppler_paths = [" in content:
            idx = content.find("poppler_paths = [")
            idx = content.find("[", idx) + 1
            idx = content.find("\n", idx)
            content = content[:idx] + f'\n{new_path_entry}' + content[idx:]
            
            with open(pdf_extractor_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated pdf_extractor.py with Poppler path")
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error updating pdf_extractor.py: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Poppler Setup for Medical Billing Validation App")
    print("=" * 60)
    print()
    
    success = setup_poppler()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Poppler setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Restart your terminal/IDE")
        print("2. Restart the Flask app: python run.py")
        print("3. Try uploading a PDF")
        sys.exit(0)
    else:
        print("⚠️  Poppler setup incomplete")
        print()
        print("Manual alternatives:")
        print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("2. Extract to: C:\\Program Files\\poppler")
        print("3. Or use the app's 'Enter Manually' tab (always works)")
        sys.exit(1)
