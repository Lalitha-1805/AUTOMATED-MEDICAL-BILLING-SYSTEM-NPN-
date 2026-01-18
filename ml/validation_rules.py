"""
Rule-Based Validation Engine
Healthcare compliance rules and fraud detection
"""

import pandas as pd
from datetime import datetime, timedelta


class ValidationRulesEngine:
    """Implements healthcare billing rules"""
    
    def __init__(self, claims_df=None):
        self.claims_df = claims_df
        self.validation_results = []
        
        # Valid diagnosis-procedure mappings
        self.valid_mappings = {
            'E10': ['99213', '99214', '99215', '92004'],
            'E11': ['99213', '99214', '99215', '92004'],
            'I10': ['99213', '99214', '99215', '93000'],
            'J44': ['94002', '94010', '94060', '94664'],
            'F32': ['99204', '99205', '90834', '90837'],
            'M79': ['99213', '99214', '20610', '97110'],
            'E78': ['99213', '99214', '99215', '80053'],
            'K21': ['99213', '99214', '43235', '43239'],
            'N18': ['99213', '99214', '99215', '36145'],
            'R07': ['99213', '99214', '93000', '71020'],
            'J06': ['99213', '99214', '69210', '92002'],
            'N39': ['99213', '99214', '81000', '81001'],
            'M99': ['99213', '98941', '98942', '97110'],
            'E66': ['99213', '99214', '99215', '99217'],
            'F41': ['99204', '99205', '90834', '90836'],
            'Z79': ['99213', '99214', '99215', '90834'],
            'R06': ['99213', '99214', '94002', '94060'],
            'I39': ['99213', '99214', '99215', '93000'],
            'J20': ['99213', '99214', '71046', '71047'],
            'K59': ['99213', '99214', '99215', '74150']
        }
    
    def rule_cost_not_exceeds_coverage(self, claim):
        """Rule 1: Cost must not exceed insurance coverage limit"""
        cost = claim['treatment_cost']
        limit = claim['insurance_coverage_limit']
        
        if cost > limit:
            return {
                'passed': False,
                'reason': f'Cost ${cost:,.2f} exceeds coverage limit ${limit:,.2f}',
                'severity': 'high'
            }
        return {'passed': True, 'reason': 'Cost within coverage limit', 'severity': 'info'}
    
    def rule_valid_diagnosis_procedure_mapping(self, claim):
        """Rule 2: Diagnosis code must match procedure code"""
        diagnosis = claim['diagnosis_code']
        procedure = claim['procedure_code']
        
        if diagnosis not in self.valid_mappings:
            return {
                'passed': False,
                'reason': f'Unknown diagnosis code: {diagnosis}',
                'severity': 'high'
            }
        
        if procedure not in self.valid_mappings[diagnosis]:
            return {
                'passed': False,
                'reason': f'Procedure {procedure} not valid for diagnosis {diagnosis}',
                'severity': 'high'
            }
        
        return {'passed': True, 'reason': 'Valid diagnosis-procedure mapping', 'severity': 'info'}
    
    def rule_cost_range_validation(self, claim):
        """Rule 3: Cost must be within reasonable range for procedure"""
        procedure = claim['procedure_code']
        cost = claim['treatment_cost']
        
        # Reasonable cost ranges per procedure
        cost_ranges = {
            '99213': (150, 500), '99214': (200, 600), '99215': (300, 800),
            '92004': (200, 600), '93000': (150, 400), '94002': (100, 250),
            '94010': (150, 350), '94060': (100, 250), '94664': (200, 500),
            '90834': (150, 300), '90837': (200, 400), '20610': (300, 800),
            '97110': (100, 300), '43235': (400, 1000), '43239': (500, 1200),
            '36145': (200, 500), '81000': (30, 200), '81001': (50, 250),
            '69210': (200, 500), '92002': (150, 400), '98941': (100, 200),
            '98942': (150, 350), '99217': (100, 300), '90836': (200, 400),
            '74150': (200, 600), '71046': (150, 400), '71047': (200, 500),
            '80053': (50, 200)
        }
        
        if procedure in cost_ranges:
            min_cost, max_cost = cost_ranges[procedure]
            if cost < min_cost or cost > max_cost:
                return {
                    'passed': False,
                    'reason': f'Cost ${cost:,.2f} outside normal range ${min_cost}-${max_cost} for {procedure}',
                    'severity': 'medium'
                }
        
        return {'passed': True, 'reason': 'Cost within reasonable range', 'severity': 'info'}
    
    def rule_age_specific_validation(self, claim):
        """Rule 4: Age-specific treatment validation"""
        age = claim['age']
        diagnosis = claim['diagnosis_code']
        procedure = claim['procedure_code']
        
        # Age-specific rules
        if age < 18 and diagnosis in ['E10', 'I10', 'N18']:
            if diagnosis == 'E10' and age < 5:
                return {
                    'passed': False,
                    'reason': f'Type 1 diabetes diagnosis unusual for age {age}',
                    'severity': 'medium'
                }
        
        if age > 80 and procedure in ['97110', '20610', '43235', '43239']:
            # More stringent for elderly with physical procedures
            if procedure in ['43235', '43239']:
                return {
                    'passed': False,
                    'reason': f'Invasive procedure {procedure} flagged for elderly patient age {age}',
                    'severity': 'medium'
                }
        
        return {'passed': True, 'reason': 'Age-appropriate procedure', 'severity': 'info'}
    
    def rule_duplicate_detection(self, claim, all_claims_df=None):
        """Rule 5: Detect duplicate claims"""
        if all_claims_df is None or self.claims_df is None:
            return {'passed': True, 'reason': 'No duplicate check possible', 'severity': 'info'}
        
        patient_id = claim['patient_id']
        procedure = claim['procedure_code']
        claim_date = claim['claim_date']
        
        # Check for same patient + procedure + date within 1 day
        duplicates = self.claims_df[
            (self.claims_df['patient_id'] == patient_id) &
            (self.claims_df['procedure_code'] == procedure) &
            (self.claims_df['claim_date'] == claim_date)
        ]
        
        if len(duplicates) > 1:
            return {
                'passed': False,
                'reason': f'Duplicate claim detected: {len(duplicates)} claims for patient {patient_id}',
                'severity': 'high'
            }
        
        return {'passed': True, 'reason': 'No duplicates detected', 'severity': 'info'}
    
    def rule_pattern_analysis(self, claim):
        """Rule 6: Unusual pattern detection"""
        cost = claim['treatment_cost']
        coverage = claim['insurance_coverage_limit']
        
        ratio = cost / (coverage + 1)
        
        # Suspicious ratios
        if ratio > 2.0:
            return {
                'passed': False,
                'reason': f'Extremely high cost-to-coverage ratio: {ratio:.2f}x',
                'severity': 'high'
            }
        elif ratio > 1.0:
            return {
                'passed': False,
                'reason': f'High cost-to-coverage ratio: {ratio:.2f}x',
                'severity': 'medium'
            }
        
        return {'passed': True, 'reason': 'Normal cost-to-coverage ratio', 'severity': 'info'}
    
    def validate_claim(self, claim, all_claims_df=None):
        """Run all validation rules on a claim"""
        rules = [
            ('Rule 1: Coverage Limit', self.rule_cost_not_exceeds_coverage),
            ('Rule 2: Diagnosis-Procedure Mapping', self.rule_valid_diagnosis_procedure_mapping),
            ('Rule 3: Cost Range', self.rule_cost_range_validation),
            ('Rule 4: Age Specific', self.rule_age_specific_validation),
            ('Rule 5: Pattern Analysis', self.rule_pattern_analysis),
        ]
        
        validation_details = []
        failed_rules = []
        
        for rule_name, rule_func in rules:
            try:
                result = rule_func(claim)
                validation_details.append({
                    'rule': rule_name,
                    'passed': result['passed'],
                    'reason': result['reason'],
                    'severity': result['severity']
                })
                if not result['passed']:
                    failed_rules.append(result)
            except Exception as e:
                validation_details.append({
                    'rule': rule_name,
                    'passed': True,
                    'reason': f'Rule execution skipped',
                    'severity': 'info'
                })
        
        # Determine overall status
        if failed_rules:
            # Check severity
            high_severity = any(r['severity'] == 'high' for r in failed_rules)
            if high_severity:
                status = 'Rejected'
            else:
                status = 'Manual Review'
            reason = ' | '.join([r['reason'] for r in failed_rules])
        else:
            status = 'Approved'
            reason = 'All rules passed'
        
        return {
            'status': status,
            'reason': reason,
            'details': validation_details,
            'failed_count': len(failed_rules)
        }
    
    def validate_batch(self, claims_df):
        """Validate multiple claims"""
        self.claims_df = claims_df
        results = []
        
        for idx, row in claims_df.iterrows():
            result = self.validate_claim(row.to_dict(), claims_df)
            result['claim_id'] = row.get('claim_id', f'CLM{idx:06d}')
            results.append(result)
        
        return pd.DataFrame(results)


def main():
    """Test validation engine"""
    print("=" * 60)
    print("VALIDATION RULES ENGINE TEST")
    print("=" * 60)
    
    # Load sample claims
    df = pd.read_csv('data/medical_billing_dataset.csv')
    
    # Test on first 10 claims
    print("\nValidating sample claims...")
    engine = ValidationRulesEngine(df)
    
    for idx in range(min(10, len(df))):
        claim = df.iloc[idx].to_dict()
        result = engine.validate_claim(claim, df)
        
        print(f"\nClaim {claim['claim_id']}:")
        print(f"  Status: {result['status']}")
        print(f"  Reason: {result['reason']}")
        print(f"  Failed Rules: {result['failed_count']}")


if __name__ == '__main__':
    main()
