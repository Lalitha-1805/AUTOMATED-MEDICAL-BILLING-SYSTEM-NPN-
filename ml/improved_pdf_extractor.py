"""
Improved PDF Bill Extractor
Enhanced text extraction and intelligent field mapping
"""

import pytesseract
from pdf2image import convert_from_path
import re
import os
from PIL import Image
import tempfile
import sys
import cv2
import numpy as np


def configure_poppler():
    """Configure Poppler PATH for PDF processing"""
    poppler_paths = [
        r'C:\Program Files\poppler\Library\bin',
        r'C:\Users\HP\Downloads\poppler-26.1.0\Library\bin',
        r'C:\Program Files (x86)\poppler\Library\bin',
        '/usr/bin',
        '/usr/local/bin',
        '/opt/homebrew/bin',
    ]
    
    for path in poppler_paths:
        if os.path.exists(path):
            if path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
            print(f"✅ Poppler PATH configured: {path}")
            return True
    
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
    """Configure pytesseract to find Tesseract executable"""
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract',
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.pytesseract_cmd = path
            print(f"Tesseract found at: {path}")
            return True
    
    try:
        result = pytesseract.get_tesseract_version()
        print(f"Tesseract accessible via PATH: {result}")
        return True
    except Exception as e:
        print(f"Warning: Could not find Tesseract: {e}")
        return False


try:
    configure_tesseract()
    configure_poppler()
except Exception as e:
    print(f"Error configuring OCR: {e}")


class ImprovedPDFBillExtractor:
    """Improved PDF extractor with better text extraction and field mapping"""
    
    def __init__(self):
        # Enhanced and comprehensive extraction patterns
        self.field_patterns = {
            'patient_id': {
                'patterns': [
                    r'(?:Patient|Member|MRN|Medical Record)\s*(?:ID|#|Number|No\.?)[\s:]*([A-Z0-9]{4,15})',
                    r'(?:Patient|Member)\s*(?:ID|#)[\s:]*([A-Z0-9]{4,15})',
                    r'(?:MRN|Patient#)[\s:]*([A-Z0-9]{4,15})',
                    r'Account\s*(?:Number|#)[\s:]*([A-Z0-9]{4,15})',
                    r'Claim\s*(?:Number|#)[\s:]*([A-Z0-9]{4,15})',
                ],
                'validation': lambda x: len(x) >= 4
            },
            'age': {
                'patterns': [
                    r'(?:Patient\s+)?Age[\s:]*(\d{1,3})',
                    r'(?:Age|DOB|Years?)[\s:]*(\d{1,3})\s*(?:years?|yrs?|y\.o\.)',
                    r'(\d{1,3})\s*(?:years?|yrs?|y\.o\.)',
                    r'DOB.*?(\d{1,3})\s*years?',
                    r'Age\s*\(years\)[\s:]*(\d{1,3})',
                ],
                'validation': lambda x: 0 < int(x) < 150
            },
            'gender': {
                'patterns': [
                    r'(?:Gender|Sex)[\s:]*([MFX]|Male|Female|Other)',
                    r'(?:Gender|Sex)[\s:]*\(([MFX])\)',
                    r'(?:Male|Female|M\.?\/F\.?)',
                ],
                'validation': lambda x: x.upper()[0] in ['M', 'F', 'X']
            },
            'diagnosis_code': {
                'patterns': [
                    r'(?:Primary\s+)?(?:Diagnosis|DX|ICD)\s*(?:Code)?[\s\(\)]*[\s:]*([A-Z0-9]{2,8})',
                    r'ICD[- ]?(?:10)?[\s:]*([A-Z][A-Z0-9]{1,7})',
                    r'Diagnosis[\s:]*([A-Z][A-Z0-9]{1,7})',
                    r'DX[\s:]*([A-Z][A-Z0-9]{1,7})',
                    r'Condition\s*Code[\s:]*([A-Z0-9]{2,8})',
                ],
                'validation': lambda x: re.match(r'[A-Z0-9]{2,8}', x.upper())
            },
            'procedure_code': {
                'patterns': [
                    r'(?:Procedure|CPT|Service)\s*(?:Code|Caode)?[\s\(\)]*[\s:]*(\d{4,5})',
                    r'(?:Procedure|Procedue)(?:Code|Caode)?[\s:]*(\d{4,5})',
                    r'CPT[\s:]*(\d{4,5})',
                    r'Procedure\s*Code[\s:]*(\d{4,5})',
                    r'Service\s*Code[\s:]*(\d{4,5})',
                    r'(?:^|\s)(\d{4,5})(?:\s+(?:procedure|cpt|code))',
                    r'Code[\s:]*(\d{4,5})(?:\s|$)',
                    r'(\d{4,5})\s*(?:procedure|cpt)',
                ],
                'validation': lambda x: re.match(r'\d{4,5}', str(x))
            },
            'treatment_cost': {
                'patterns': [
                    r'(?:Treatment|Total|Bill|Charge|Billed)\s*(?:Cost|Amount|Due|)?[\s\(\$\)]*[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Total\s+(?:Cost|Charges|Due|Amount|Billed Amount)[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Amount\s+Due[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Bill(?:ed)?\s+Amount[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'(?:Total\s+)?Billed[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Professional\s+Fee[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Service\s+Fee[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Cost[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Treatment[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'\$[\s]*(\d+[.,]?\d*)(?:\s*(?:total|due|amount|charge|cost|billed))?',
                    r'(\d{2,5})(?:\s+(?:total|cost|due|amount|charges|billed))',
                    r'(?:Total|Billed).*?(\d{2,5})(?:[^0-9]|$)',
                ],
                'validation': lambda x: 50 <= float(str(x).replace(',', '')) <= 100000
            },
            'insurance_coverage_limit': {
                'patterns': [
                    r'(?:Insurance\s+)?Coverage\s+Limit[\s\(\$\)]*[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Maximum\s+(?:Benefit|Coverage)[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Plan\s+Maximum[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Coverage\s+Amount[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Limit[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Annual\s+Limit[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Insurance[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'Coverage[\s:]*\$?[\s]*(\d+[.,]?\d*)',
                    r'(\d{4,6})(?:\s+(?:coverage|limit|maximum|benefit))',
                ],
                'validation': lambda x: 100 <= float(str(x).replace(',', '')) <= 1000000
            },
            'hospital_id': {
                'patterns': [
                    r'(?:Hospital|Facility|Provider|Healthcare)\s*(?:ID|Code)[\s:]*([A-Z0-9]{3,10})',
                    r'(?:Facility|Provider)\s*(?:ID|#)[\s:]*([A-Z0-9]{3,10})',
                    r'Hospital[\s:]*([A-Z0-9]{3,10})',
                    r'Institution[\s:]*([A-Z0-9]{3,10})',
                ],
                'validation': lambda x: len(x) >= 3
            },
        }
    
    def preprocess_image(self, image):
        """Enhance image for better OCR"""
        try:
            # Convert PIL image to cv2 format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Apply image enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(cv_image)
            
            # Apply thresholding for better text extraction
            _, binary = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY)
            
            # Convert back to PIL
            return Image.fromarray(binary)
        except:
            # If enhancement fails, return original
            return image
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF with enhanced preprocessing"""
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not os.access(pdf_path, os.R_OK):
                raise PermissionError(f"PDF file is not readable: {pdf_path}")
            
            # Convert PDF pages to images with higher DPI
            images = convert_from_path(pdf_path, dpi=300)
            
            if not images:
                raise ValueError("PDF has no pages or could not be read")
            
            extracted_text = ""
            
            for page_num, image in enumerate(images, 1):
                try:
                    # Preprocess image for better OCR
                    enhanced_image = self.preprocess_image(image)
                    
                    # Extract text with Tesseract config for better accuracy
                    text = pytesseract.image_to_string(
                        enhanced_image,
                        config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ()-.,/$:'
                    )
                    
                    if text.strip():
                        extracted_text += text + "\n"
                        
                except Exception as e:
                    print(f"Warning: Error extracting text from page {page_num}: {e}")
                    continue
            
            if not extracted_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Clean up extracted text
            extracted_text = self._clean_text(extracted_text)
            
            return extracted_text
        
        except FileNotFoundError as e:
            print(f"File Error: {e}")
            return ""
        except Exception as e:
            print(f"PDF Error: {e}")
            return ""
    
    def _clean_text(self, text):
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('$', '$')
        text = text.replace('l0', '10')  # Common OCR error: lowercase L as zero
        text = text.replace('O0', '00')  # Common OCR error: uppercase O as zero
        
        return text.strip()
    
    def extract_field(self, text, field_name):
        """Extract a specific field using intelligent pattern matching"""
        if field_name not in self.field_patterns:
            return None
        
        field_config = self.field_patterns[field_name]
        patterns = field_config['patterns']
        validation = field_config['validation']
        
        # Try each pattern
        for pattern in patterns:
            try:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
                if not matches:
                    continue
                
                # Process all matches, prioritize by position
                for match in matches:
                    try:
                        value = match.group(1).strip() if match.lastindex and match.lastindex >= 1 else None
                        
                        if not value:
                            continue
                        
                        # Normalize value
                        if field_name == 'gender':
                            value = value.upper()[0] if value else None
                            if not value:
                                continue
                        elif field_name in ['age', 'procedure_code']:
                            value = ''.join(c for c in value if c.isdigit())
                            if not value:
                                continue
                        elif field_name in ['treatment_cost', 'insurance_coverage_limit']:
                            # Remove common OCR errors and currency symbols
                            value = str(value).replace(',', '').replace('$', '').replace('O', '0').replace('l', '1').strip()
                            try:
                                value = float(value)
                            except ValueError:
                                continue
                        elif field_name == 'diagnosis_code':
                            value = value.upper()
                        
                        # Validate
                        if validation(value):
                            return value
                    except (ValueError, IndexError, AttributeError) as e:
                        continue
            except Exception as e:
                continue
        
        return None
    
    def extract_all_fields(self, pdf_path):
        """Extract all fields from PDF"""
        print(f"\n📄 Extracting fields from: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text or text.strip() == '':
            return {
                'success': False,
                'error': 'Could not extract text from PDF. Ensure it has readable text content.',
                'extracted_text': ''
            }
        
        print(f"✓ Extracted {len(text)} characters from PDF")
        
        # Extract all fields
        extracted_data = {
            'success': True,
            'extracted_text': text[:2000],  # First 2000 chars for reference
            'patient_id': self.extract_field(text, 'patient_id'),
            'age': self.extract_field(text, 'age'),
            'gender': self.extract_field(text, 'gender'),
            'diagnosis_code': self.extract_field(text, 'diagnosis_code'),
            'procedure_code': self.extract_field(text, 'procedure_code'),
            'treatment_cost': self.extract_field(text, 'treatment_cost'),
            'insurance_coverage_limit': self.extract_field(text, 'insurance_coverage_limit'),
            'hospital_id': self.extract_field(text, 'hospital_id'),
        }
        
        # Log extraction results
        print("\n📋 Extraction Results:")
        for field, value in extracted_data.items():
            if field not in ['success', 'extracted_text']:
                status = "✓" if value is not None else "✗"
                print(f"  {status} {field}: {value}")
        
        return extracted_data


# Create singleton instance
pdf_extractor = ImprovedPDFBillExtractor()


def allowed_file(filename):
    """Check if file is allowed (PDF only)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

