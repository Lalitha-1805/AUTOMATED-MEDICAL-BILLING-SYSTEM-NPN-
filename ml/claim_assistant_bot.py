"""
Claim Assistance Bot - Explains validation outcomes to users
This module interprets ValidationReport data and provides user-friendly explanations.

IMPORTANT: This bot ONLY explains existing validation results.
It does NOT perform validation, predict fraud, or modify decisions.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple


class ClaimAssistanceBot:
    """
    Interprets and explains claim validation outcomes.
    Provides supportive, professional guidance based on system decisions.
    """

    # Fraud risk score interpretations
    RISK_INTERPRETATIONS = {
        (0, 10): ("Very Low", "Your claim shows minimal fraud indicators."),
        (11, 25): ("Low", "Your claim appears standard with no major concerns."),
        (26, 50): ("Moderate", "Your claim has some factors that require review."),
        (51, 75): ("High", "Your claim contains patterns that warrant closer examination."),
        (76, 100): ("Very High", "Your claim presents significant risk factors requiring investigation."),
    }

    def __init__(self):
        """Initialize the claim assistance bot."""
        self.timestamp = datetime.now()

    @staticmethod
    def _get_risk_level(fraud_score: float) -> Tuple[str, str]:
        """
        Interpret fraud risk score in plain language.
        
        Args:
            fraud_score: Score from 0-100
            
        Returns:
            Tuple of (risk_level, explanation)
        """
        for (low, high), (level, explanation) in ClaimAssistanceBot.RISK_INTERPRETATIONS.items():
            if low <= fraud_score <= high:
                return level, explanation
        return "Unknown", "Unable to interpret risk score."

    def format_violations(self, violations: list) -> str:
        """Convert violation codes to user-friendly explanations."""
        violation_explanations = {
            "INVALID_DIAGNOSIS": "Diagnosis code is not recognized in the medical database.",
            "INVALID_PROCEDURE": "Procedure code is invalid or not found in records.",
            "COST_EXCEEDS_LIMIT": "Claimed amount exceeds the coverage limit for this service.",
            "MISMATCH_DIAGNOSIS_PROCEDURE": "The procedure does not match the diagnosis.",
            "DUPLICATE_CLAIM": "This claim appears to be a duplicate of a previous submission.",
            "AGE_RESTRICTION": "This treatment is not covered for the patient's age group.",
            "MISSING_AUTHORIZATION": "Prior authorization documentation is missing.",
            "INVALID_PROVIDER": "Healthcare provider is not in the network.",
            "COVERAGE_EXPIRED": "Coverage period has expired for this claim.",
            "COST_TO_COVERAGE_RATIO": "The cost-to-coverage ratio exceeds acceptable thresholds.",
            "ANOMALY_DETECTED": "Unusual patterns detected in this claim.",
            "MISSING_DOCUMENTATION": "Required supporting documents are not attached.",
        }
        
        formatted = []
        for violation in violations:
            explanation = violation_explanations.get(
                violation.upper(),
                violation
            )
            formatted.append(f"• {explanation}")
        
        return "\n".join(formatted) if formatted else "• No specific violations recorded."

    def generate_response(self, claim_data: Dict, validation_report: Dict) -> Dict:
        """
        Generate user-friendly explanation of claim validation.
        
        Args:
            claim_data: Claim details from database
            validation_report: ValidationReport containing approval status, violations, fraud score
            
        Returns:
            Dictionary with structured response following mandatory format
        """
        
        # Extract key data
        status = validation_report.get("status", "UNKNOWN").upper()
        fraud_score = validation_report.get("fraud_risk_score", 0)
        violations = validation_report.get("violations", [])
        anomaly_flags = validation_report.get("anomaly_flags", [])
        missing_documents = validation_report.get("missing_documents", [])
        
        # ========== 1️⃣ SUMMARY ==========
        if status == "APPROVED":
            summary = f"✅ Your claim #{claim_data.get('claim_id', 'N/A')} has been APPROVED for processing."
        elif status == "REJECTED":
            summary = f"❌ Your claim #{claim_data.get('claim_id', 'N/A')} has been REJECTED and requires corrections."
        elif status == "PENDING":
            summary = f"⏳ Your claim #{claim_data.get('claim_id', 'N/A')} is under REVIEW and awaiting final decision."
        else:
            summary = f"Your claim #{claim_data.get('claim_id', 'N/A')} status: {status}"

        # ========== 2️⃣ ISSUES IDENTIFIED ==========
        issues = []
        
        if violations:
            issues.append("**Rule Violations:**")
            issues.append(self.format_violations(violations))
        
        if anomaly_flags:
            issues.append("\n**Anomaly Flags:**")
            for flag in anomaly_flags:
                issues.append(f"• {flag}")
        
        if missing_documents:
            issues.append("\n**Missing Documents:**")
            for doc in missing_documents:
                issues.append(f"• {doc}")
        
        issues_text = "\n".join(issues) if issues else "No issues identified."

        # ========== 3️⃣ FRAUD RISK EXPLANATION ==========
        risk_level, risk_explanation = self._get_risk_level(fraud_score)
        fraud_risk_text = (
            f"**Fraud Risk Score: {fraud_score}/100 ({risk_level})**\n"
            f"{risk_explanation}\n\n"
            f"This score is calculated based on patterns in your claim compared to "
            f"typical medical billing records. It does not indicate actual fraud, "
            f"but helps identify claims that may need additional review."
        )

        # ========== 4️⃣ REQUIRED ACTIONS ==========
        actions = []
        
        if status == "REJECTED":
            actions.append("To resubmit your claim, please:")
            if violations:
                actions.append("1. **Address Rule Violations:** Review and correct the issues listed above.")
            if missing_documents:
                actions.append("2. **Attach Missing Documents:** Gather and upload all required documentation.")
            actions.append("3. **Resubmit:** After corrections, resubmit the claim through the portal.")
        elif status == "PENDING":
            actions.append("Your claim is being reviewed. No action is required at this time.")
            actions.append("You will receive a notification once the review is complete.")
        elif status == "APPROVED":
            actions.append("No action required. Your claim is approved and will be processed for payment.")
        
        actions_text = "\n".join(actions)

        # ========== BUILD FINAL RESPONSE ==========
        response = {
            "claim_id": claim_data.get("claim_id", "N/A"),
            "timestamp": datetime.now().isoformat(),
            "status": status,
            
            # Structured response components
            "summary": summary,
            "issues": issues_text,
            "fraud_risk": fraud_risk_text,
            "required_actions": actions_text,
            
            # Full formatted response for display
            "full_response": self._format_full_response(
                summary, issues_text, fraud_risk_text, actions_text
            ),
            
            # Metadata
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "has_violations": bool(violations),
            "has_anomalies": bool(anomaly_flags),
            "has_missing_docs": bool(missing_documents),
        }
        
        return response

    @staticmethod
    def _format_full_response(summary: str, issues: str, fraud_risk: str, actions: str) -> str:
        """Format response for display."""
        return f"""
{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**2️⃣ Issues Identified**
{issues}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**3️⃣ Fraud Risk Explanation**
{fraud_risk}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**4️⃣ Required Actions**
{actions}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    def handle_user_question(self, question: str, claim_data: Dict, validation_report: Dict) -> str:
        """
        Handle specific user questions about their claim.
        
        Args:
            question: User's question
            claim_data: Claim details
            validation_report: Validation report
            
        Returns:
            User-friendly answer
        """
        question_lower = question.lower()
        
        # Categorize questions
        if any(word in question_lower for word in ["why", "rejected", "denied", "flagged"]):
            return self._answer_rejection_question(claim_data, validation_report)
        
        elif any(word in question_lower for word in ["rule", "violation", "incorrect"]):
            return self._answer_violation_question(validation_report)
        
        elif any(word in question_lower for word in ["document", "missing", "attach"]):
            return self._answer_missing_docs_question(validation_report)
        
        elif any(word in question_lower for word in ["fraud", "risk", "score", "anomaly"]):
            return self._answer_fraud_risk_question(validation_report)
        
        elif any(word in question_lower for word in ["reduce", "improve", "fix", "correct"]):
            return self._answer_correction_question(validation_report)
        
        elif any(word in question_lower for word in ["medical", "diagnosis", "treatment"]):
            return "This assistant can only help with claim validation and correction queries. For medical questions, please consult your healthcare provider."
        
        elif any(word in question_lower for word in ["legal", "dispute", "appeal", "policy"]):
            return "This assistant can only help with claim validation and correction queries. For policy disputes or legal concerns, please contact your insurance provider directly."
        
        else:
            return "This assistant can only help with claim validation and correction queries. Please ask about your claim status, violations, missing documents, or fraud risk score."

    @staticmethod
    def _answer_rejection_question(claim_data: Dict, validation_report: Dict) -> str:
        """Answer: Why was my claim rejected?"""
        status = validation_report.get("status", "UNKNOWN").upper()
        violations = validation_report.get("violations", [])
        
        if status == "APPROVED":
            return "Your claim has been approved. There is no rejection to explain."
        
        if not violations:
            return "No specific violations were recorded for this claim. Please contact support for more details."
        
        bot = ClaimAssistanceBot()
        violation_list = bot.format_violations(violations)
        
        return f"""Your claim was not approved due to the following rule violations:

{violation_list}

To address this, review each violation and make the necessary corrections before resubmitting."""

    @staticmethod
    def _answer_violation_question(validation_report: Dict) -> str:
        """Answer: What rule violations were detected?"""
        violations = validation_report.get("violations", [])
        
        if not violations:
            return "No rule violations were detected in your claim."
        
        bot = ClaimAssistanceBot()
        violation_list = bot.format_violations(violations)
        
        return f"""The following rule violations were identified:

{violation_list}

Each violation indicates a discrepancy with medical billing standards or your coverage policy."""

    @staticmethod
    def _answer_missing_docs_question(validation_report: Dict) -> str:
        """Answer: What documents are missing?"""
        missing_docs = validation_report.get("missing_documents", [])
        
        if not missing_docs:
            return "All required documents appear to be attached to your claim."
        
        docs_list = "\n".join([f"• {doc}" for doc in missing_docs])
        
        return f"""The following documents are missing or incomplete:

{docs_list}

Please gather these documents and attach them to your claim before resubmitting."""

    @staticmethod
    def _answer_fraud_risk_question(validation_report: Dict) -> str:
        """Answer: What does my fraud risk score mean?"""
        fraud_score = validation_report.get("fraud_risk_score", 0)
        bot = ClaimAssistanceBot()
        risk_level, risk_explanation = bot._get_risk_level(fraud_score)
        
        return f"""Your Fraud Risk Score: {fraud_score}/100 ({risk_level})

{risk_explanation}

This score is generated by analyzing patterns in your claim against millions of medical billing records. 
A higher score means your claim has characteristics that require additional review—not that fraud has been proven.

Common factors that may increase the score:
• Unusual treatment combinations
• High claim amounts compared to similar cases
• Multiple related claims in short timeframes
• Uncommon diagnosis-procedure pairs

This is an automated assessment tool designed to protect both patients and insurers."""

    @staticmethod
    def _answer_correction_question(validation_report: Dict) -> str:
        """Answer: How can I reduce my fraud risk score or fix my claim?"""
        violations = validation_report.get("violations", [])
        missing_docs = validation_report.get("missing_documents", [])
        
        corrections = []
        
        if violations:
            corrections.append("**1. Address Rule Violations:**")
            corrections.append("   - Review each violation listed in your claim report")
            corrections.append("   - Correct any data entry errors (codes, amounts, dates)")
            corrections.append("   - Verify diagnosis and procedure codes are accurate")
        
        if missing_docs:
            corrections.append("\n**2. Attach Missing Documents:**")
            corrections.append("   - Medical records supporting the diagnosis")
            corrections.append("   - Itemized bills from the healthcare provider")
            corrections.append("   - Proof of authorization (if required)")
            corrections.append("   - Insurance coverage details")
        
        corrections.append("\n**3. Review for Accuracy:**")
        corrections.append("   - Double-check patient information")
        corrections.append("   - Verify treatment dates are within coverage period")
        corrections.append("   - Ensure all service providers are in-network")
        
        corrections.append("\n**4. Resubmit:**")
        corrections.append("   - After corrections, resubmit your claim through the portal")
        corrections.append("   - Keep records of all changes made")
        
        if not violations and not missing_docs:
            corrections.append("Your claim appears complete. If the fraud score is high due to unusual patterns,")
            corrections.append("consider providing additional context or medical documentation.")
        
        return "\n".join(corrections)


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def get_claim_explanation(claim_data: Dict, validation_report: Dict) -> Dict:
    """
    Helper function to get claim explanation.
    Usage: from ml.claim_assistant_bot import get_claim_explanation
    
    result = get_claim_explanation(claim, report)
    print(result['full_response'])
    """
    bot = ClaimAssistanceBot()
    return bot.generate_response(claim_data, validation_report)
