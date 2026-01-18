"""
PDF Bill Extractor
Extracts text and relevant fields from medical bills (PDF)
"""

import pytesseract
from pdf2image import convert_from_path
import re
import os
from PIL import Image
import tempfile
import sys


def configure_poppler():
    """
    Configure Poppler PATH for PDF processing.
    Handles various installation locations and directories.
    """
    # Try possible Poppler locations
    poppler_paths = [
        r'C:\Program Files\poppler\Library\bin',  # Standard Windows installation
        r'C:\Users\HP\Downloads\poppler-26.1.0\Library\bin',  # Downloads folder (v26.1.0)
        r'C:\Program Files (x86)\poppler\Library\bin',  # 32-bit Windows
        '/usr/bin',  # Linux
        '/usr/local/bin',  # macOS
        '/opt/homebrew/bin',  # macOS M1/M2
    ]
    
    # Try to find Poppler in PATH via system
    for path in poppler_paths:
        if os.path.exists(path):
            if path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
            print(f"✅ Poppler PATH configured: {path}")
            return True
    
    # If not found, try to verify via pdftoppm command
    try:
        import subprocess
        result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"✅ Poppler found in system PATH")
            return True
    except:
        pass
    
    print("⚠️  Poppler not found in standard locations")
    return False


def configure_tesseract():
    """
    Configure pytesseract to find Tesseract executable.
    Works for Windows, Linux, and macOS installations.
    """
    # Try to find Tesseract in common locations
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows default
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # Windows 32-bit
        '/usr/bin/tesseract',  # Linux
        '/usr/local/bin/tesseract',  # macOS Homebrew
        '/opt/homebrew/bin/tesseract',  # macOS M1/M2 Homebrew
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.pytesseract_cmd = path
            print(f"Tesseract found at: {path}")
            return True
    
    # If not found, try system PATH
    try:
        result = pytesseract.get_tesseract_version()
        print(f"Tesseract accessible via PATH: {result}")
        return True
    except Exception as e:
        print(f"Warning: Could not find Tesseract: {e}")
        print("Tesseract OCR must be installed separately.")
        print("Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def check_poppler():
    """
    Check if Poppler is installed for PDF processing.
    """
    poppler_paths = [
        r'C:\Program Files\poppler\Library\bin',  # Windows Chocolatey
        r'C:\Program Files (x86)\poppler\bin',  # Windows alternative
        '/usr/bin',  # Linux default
        '/usr/local/bin',  # macOS Homebrew
        '/opt/homebrew/bin',  # macOS M1/M2
    ]
    
    for path in poppler_paths:
        if os.path.exists(path):
            # Add to PATH if not already there
            if path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
            return True
    
    return False


# Configure on module load
try:
    configure_tesseract()
    poppler_available = check_poppler()
    if not poppler_available:
        print("Warning: Poppler not found in standard paths. PDF extraction may not work.")
        print("Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
except Exception as e:
    print(f"Error configuring OCR: {e}")


class PDFBillExtractor:
    """Extract information from PDF medical bills"""
    
    def __init__(self):
        # Configure Poppler and Tesseract on initialization
        configure_poppler()
        configure_tesseract()
        
        # Common cost patterns (amounts in dollars) - ENHANCED
        self.cost_patterns = [
            r'Treatment Cost\s*\(\$\)[\s:]*(\d[,\d]*\.?\d*)',  # Treatment Cost ($): 4500
            r'Total Cost[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Total Due[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Bill Amount[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Amount Due[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Total Charges[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Cost[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Charge\s+(?:Amount)?[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Professional Fee[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'Service Fee[:\s]*\$?(\d[,\d]*\.?\d*)',
            r'\$(\d[,\d]*\.?\d*)\s*(?:total|due|amount|charge)',
            r'Net\s+(?:Amount)?[:\s]*\$?(\d[,\d]*\.?\d*)',
        ]
        
        # Common diagnosis code patterns (ICD-10 or numeric codes) - ENHANCED
        self.diagnosis_patterns = [
            r'Diagnosis Code\s*\(ICD\)[\s:]*([A-Z0-9]{1,8}?)(?:\s|—|$)',  # Match code before description
            r'Diagnosis\s*(?:Code)?[\s:]*([A-Z0-9]{1,8}?)(?:\s|—|:|$)',
            r'ICD[- ]?(?:10)?[\s:]*([A-Z0-9]{1,8})',
            r'DX[\s:]*([A-Z0-9]{1,8})',
            r'Condition[\s:]*\(([A-Z0-9]{1,8})\)',
            r'Primary\s+Diagnosis[\s:]*([A-Z0-9]{1,8})',
        ]
        
        # Common procedure code patterns (CPT) - ENHANCED
        self.procedure_patterns = [
            r'(?:Procedure|CPT|Code)[\s\(\w\)]*[\s:]*(\d{4,5})',  # Match CPT: 93000 or similar
            r'Procedure Code[\s\(\w\)]*[\s:]*(\d{4,5})',  # Procedure Code (CPT): 93000
            r'CPT Code[\s:]*(\d{4,5})',
            r'Service Code[\s:]*(\d{4,5})',
            r'Procedural Code[\s:]*(\d{4,5})',
            r'Medical Code[\s:]*(\d{4,5})',
            r'Service ID[\s:]*(\d{4,5})',
        ]
        
        # Coverage limit patterns - ENHANCED
        self.coverage_patterns = [
            r'Insurance Coverage Limit\s*\(\$\)[\s:]*(\d[,\d]*\.?\d*)',  # Insurance Coverage Limit ($): 2000
            r'(?:Coverage|Benefit)[\s]*Limit[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Insurance Coverage[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Maximum Benefit[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Coverage Amount[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Limit[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Plan Maximum[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Annual Limit[\s:]*\$?(\d[,\d]*\.?\d*)',
            r'Deductible[\s:]*\$?(\d[,\d]*\.?\d*)',
        ]
        
        # Patient ID patterns - ENHANCED
        self.patient_id_patterns = [
            r'(?:Patient|Member)\s*ID[\s:]*([A-Z0-9]{4,12})',
            r'Patient Number[\s:]*([A-Z0-9]{4,12})',
            r'ID[\s:]*([A-Z0-9]{4,12})',
            r'Patient Ref[\s:]*([A-Z0-9]{4,12})',
            r'Account[\s]*Number[\s:]*([A-Z0-9]{4,12})',
        ]
        
        # Age patterns - ENHANCED
        self.age_patterns = [
            r'Age[\s:]*(\d{1,3})',
            r'Patient Age[\s:]*(\d{1,3})',
            r'DOB.*?(\d{1,3})\s*years?',
            r'Age\s+\(years\)[\s:]*(\d{1,3})',
            r'(\d{1,3})\s*(?:years?|yrs?)\s+old',
        ]
        
        # Gender patterns - ENHANCED
        self.gender_patterns = [
            r'Gender[\s:]*([MFX])',
            r'Sex[\s:]*([MFX])',
            r'Patient Sex[\s:]*([MFX])',
            r'Gender[\s:]*\(([MF])\)',
            r'(?:Male|Female|M|F)',
        ]
        
        # Hospital ID patterns - ENHANCED
        self.hospital_patterns = [
            r'Hospital\s*ID[\s:]*([A-Z0-9]{3,8})',
            r'Facility[\s]*ID[\s:]*([A-Z0-9]{3,8})',
            r'Provider[\s]*ID[\s:]*([A-Z0-9]{3,8})',
            r'Hospital[\s]*Code[\s:]*([A-Z0-9]{3,8})',
            r'Healthcare Facility[\s:]*([A-Z0-9]{3,8})',
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF file using OCR
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            # First check if file exists and is readable
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not os.access(pdf_path, os.R_OK):
                raise PermissionError(f"PDF file is not readable: {pdf_path}")
            
            # Convert PDF pages to images
            try:
                images = convert_from_path(pdf_path)
            except Exception as e:
                error_msg = str(e)
                if 'poppler' in error_msg.lower() or 'page count' in error_msg.lower():
                    raise RuntimeError(
                        f"Poppler is not installed or not in PATH. "
                        f"Poppler is required for PDF conversion. "
                        f"Install from: https://github.com/oschwartz10612/poppler-windows/releases/ "
                        f"(Windows) or 'apt-get install poppler-utils' (Linux) or 'brew install poppler' (macOS). "
                        f"Original error: {error_msg}"
                    )
                else:
                    raise RuntimeError(f"Failed to convert PDF to images: {error_msg}. PDF may be corrupted or invalid.")
            
            if not images:
                raise ValueError("PDF has no pages or could not be read")
            
            extracted_text = ""
            for page_num, image in enumerate(images, 1):
                try:
                    # Use OCR to extract text
                    text = pytesseract.image_to_string(image)
                    if text.strip():  # Only add if text was actually extracted
                        extracted_text += text + "\n"
                except Exception as e:
                    print(f"Warning: Error extracting text from page {page_num}: {e}")
                    continue
            
            # Check if any text was extracted
            if not extracted_text.strip():
                raise ValueError(
                    "No text could be extracted from PDF. This may mean: "
                    "1) PDF is a pure image with no OCR, "
                    "2) Tesseract OCR is not properly installed, "
                    "3) PDF is encrypted or corrupted. "
                    "Try uploading a clearer PDF or a PDF with a text layer."
                )
            
            return extracted_text
        
        except FileNotFoundError as e:
            print(f"File Error: {e}")
            return ""
        except PermissionError as e:
            print(f"Permission Error: {e}")
            return ""
        except ValueError as e:
            print(f"Extraction Error: {e}")
            return ""
        except RuntimeError as e:
            print(f"PDF Error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error extracting PDF: {e}")
            return ""
    
    def extract_cost(self, text):
        """Extract treatment cost from text with improved accuracy"""
        for pattern in self.cost_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        # Check if pattern has capture groups
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        # Sanity check: medical bills are typically $50-$100,000
                        if 50 <= amount <= 100000:
                            return amount
                    except (IndexError, ValueError):
                        pass
            except:
                pass
        return None
    
    def extract_diagnosis_code(self, text):
        """Extract diagnosis (ICD-10) code from text with improved matching"""
        for pattern in self.diagnosis_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        code = match.group(1).upper().strip()
                        # Valid ICD-10 format: Letter + 2+ digits
                        if re.match(r'[A-Z]\d{2,}', code) or re.match(r'[A-Z0-9]{3,8}', code):
                            return code[:8]  # Limit to 8 chars
                    except (IndexError, AttributeError):
                        pass
            except:
                pass
        return None
    
    def extract_procedure_code(self, text):
        """Extract procedure (CPT) code from text with improved matching"""
        for pattern in self.procedure_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        code = match.group(1)
                        # Valid CPT format: 4-5 digits
                        if re.match(r'\d{4,5}', code):
                            return code
                    except (IndexError, AttributeError):
                        pass
            except:
                pass
        return None
    
    def extract_coverage_limit(self, text):
        """Extract insurance coverage limit from text"""
        for pattern in self.coverage_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        # Sanity check
                        if 100 <= amount <= 1000000:
                            return amount
                    except (IndexError, ValueError):
                        pass
            except:
                pass
        return None
    
    def extract_patient_id(self, text):
        """Extract patient ID from text"""
        for pattern in self.patient_id_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        patient_id = match.group(1)
                        if len(patient_id) >= 4:
                            return patient_id
                    except (IndexError, AttributeError):
                        pass
            except:
                pass
        return None
    
    def extract_age(self, text):
        """Extract patient age from text"""
        for pattern in self.age_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        age = int(match.group(1))
                        # Sanity check
                        if 0 < age < 150:
                            return age
                    except (IndexError, ValueError):
                        pass
            except:
                pass
        return None
    
    def extract_gender(self, text):
        """Extract patient gender from text"""
        for pattern in self.gender_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        gender = match.group(1).upper()
                        if gender in ['M', 'F', 'X']:
                            return gender
                    except (IndexError, AttributeError):
                        pass
            except:
                pass
        return None
    
    def extract_hospital_id(self, text):
        """Extract hospital ID from text"""
        for pattern in self.hospital_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        hospital_id = match.group(1)
                        if len(hospital_id) >= 3:
                            return hospital_id
                    except (IndexError, AttributeError):
                        pass
            except:
                pass
        return None
    
    def extract_all_fields(self, pdf_path):
        """
        Extract all relevant fields from PDF bill
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted fields
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text or text.strip() == '':
            return {
                'success': False,
                'error': (
                    'Could not extract text from PDF. This may mean:\n'
                    '1. PDF is mostly images without a text layer\n'
                    '2. PDF is corrupted or not a valid medical bill\n'
                    '3. Tesseract OCR needs better PDF quality\n\n'
                    'Solutions:\n'
                    '- Try uploading a clearer/higher quality PDF\n'
                    '- Ensure PDF is a document (not just an image)\n'
                    '- Use the "Enter Manually" tab to input fields directly'
                )
            }
        
        # Extract all fields
        extracted_data = {
            'success': True,
            'extracted_text': text[:1000] if len(text) > 1000 else text,  # First 1000 chars for reference
            'patient_id': self.extract_patient_id(text),
            'age': self.extract_age(text),
            'gender': self.extract_gender(text),
            'diagnosis_code': self.extract_diagnosis_code(text),
            'procedure_code': self.extract_procedure_code(text),
            'treatment_cost': self.extract_cost(text),
            'insurance_coverage_limit': self.extract_coverage_limit(text),
            'hospital_id': self.extract_hospital_id(text),
        }
        
        return extracted_data


def allowed_file(filename):
    """Check if file is allowed (PDF)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'
