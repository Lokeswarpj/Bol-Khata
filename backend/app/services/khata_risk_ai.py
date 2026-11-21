"""
BolKhata - "Khata Risk AI" Predictive Bad-Debt Protection Engine
Analyzes customer debt velocity, repayment delays, and balance ratios to warn
Kirana merchants before extending risky credit.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime


class KhataRiskAI:
    """Predictive credit risk analytics for Kirana accounts."""

    @classmethod
    def evaluate_customer_risk(
        cls,
        customer_name: str,
        current_balance: float,
        transactions: List[Any],
        new_credit_amount: float = 0.0,
        language: str = "hi-IN"
    ) -> Dict[str, Any]:
        """
        Calculates bad-debt risk level, risk score, and proactive audio warning.
        """
        total_balance = max(0.0, float(current_balance) + float(new_credit_amount))
        
        # Calculate days since last payment
        last_payment_date: Optional[date] = None
        consecutive_credits = 0
        total_credit_sum = 0.0
        total_payment_sum = 0.0

        for t in transactions:
            direction = getattr(t, "direction", "")
            amt = getattr(t, "amount", 0.0)
            t_date = getattr(t, "transaction_date", None)

            if direction == "credit":
                total_credit_sum += amt
                consecutive_credits += 1
            elif direction == "payment":
                total_payment_sum += amt
                consecutive_credits = 0
                if t_date and (last_payment_date is None or t_date > last_payment_date):
                    last_payment_date = t_date

        days_overdue = 0
        if last_payment_date:
            days_overdue = (date.today() - last_payment_date).days
        elif transactions:
            # Has transactions but never paid
            first_txn_date = getattr(transactions[0], "transaction_date", date.today())
            days_overdue = (date.today() - first_txn_date).days

        # Risk Score Calculation (0 to 100)
        # Factors:
        # - High balance (> ₹1500)
        # - Long overdue (> 21 days)
        # - Low repayment ratio
        # - Many consecutive credits without payment
        risk_score = 10  # baseline
        reasons = []

        if total_balance > 2500:
            risk_score += 35
            reasons.append(f"High balance of ₹{int(total_balance)}")
        elif total_balance > 1000:
            risk_score += 20
            reasons.append(f"Balance above ₹1,000")

        if days_overdue >= 30:
            risk_score += 40
            reasons.append(f"No payments in {days_overdue} days")
        elif days_overdue >= 14:
            risk_score += 25
            reasons.append(f"{days_overdue} days since last payment")

        if consecutive_credits >= 3:
            risk_score += 15
            reasons.append(f"{consecutive_credits} credit entries without any payment")

        risk_score = min(100, risk_score)

        if risk_score >= 60:
            risk_level = "HIGH RISK"
            color = "rose"
        elif risk_score >= 35:
            risk_level = "MODERATE"
            color = "amber"
        else:
            risk_level = "LOW RISK"
            color = "emerald"

        # Generate vernacular proactive warning
        warning_voice_text = cls._build_warning_text(
            customer_name, risk_level, total_balance, days_overdue, language
        )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "badge_color": color,
            "current_balance": total_balance,
            "days_overdue": days_overdue,
            "reasons": reasons,
            "warning_voice": warning_voice_text,
            "recommendation": (
                f"Collect ₹{int(current_balance)} before adding new credit"
                if risk_level == "HIGH RISK"
                else "Normal credit risk"
            )
        }

    @staticmethod
    def _build_warning_text(name: str, level: str, balance: float, days: int, lang: str) -> Optional[str]:
        if level != "HIGH RISK":
            return None

        bal_str = f"₹{int(balance)}"
        if lang.startswith("kn"):
            return f"ಎಚ್ಚರಿಕೆ! {name} ಅವರ ಒಟ್ಟು ಬಾಕಿ {bal_str} ಆಗಿದೆ ಮತ್ತು {days} ದಿನಗಳಿಂದ ಯಾವುದೇ ಪಾವತಿ ಬಂದಿಲ್ಲ. ಹೊಸ ಸಾಲ ಕೊಡುವ ಮುನ್ನ ಪರಿಶೀಲಿಸಿ."
        elif lang.startswith("te"):
            return f"హెచ్చరిక! {name} గారి మొత్తం బాకీ {bal_str} అయింది. {days} రోజులుగా ఎలాంటి చెల్లింపు రాలేదు."
        elif lang.startswith("hi"):
            return f"Savdhan! {name} ka kul baaki {bal_str} ho gaya hai aur pichle {days} dino se koi jama nahi hua. Naya udhaar dene se pehle pichla hisaab check kijiye."
        else:
            return f"Credit Warning! {name} has an overdue balance of {bal_str} with no payment for {days} days."


khata_risk_ai = KhataRiskAI()
evaluate_customer_risk = KhataRiskAI.evaluate_customer_risk

