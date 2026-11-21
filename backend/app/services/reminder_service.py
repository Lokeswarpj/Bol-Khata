"""
BolKhata - Responsible AI & Compliance Guardrails: Polite Reminders Service
Strictly complies with Hackathon Track Rules:
1. Reminders go ONLY to customers who explicitly opted in (opted_in_reminders == True).
2. Absolutely NO pressure, harassment, legal threats, or lending/interest language.
3. Polite, respectful, culturally appropriate tone in Hindi and Indian English.
4. DPDP Act compliance validation.
"""

import re
from typing import Optional, Dict, Any, List
from app.models import Customer


# Prohibited words/phrases to prevent any harassment or pressure language
BANNED_PRESSURE_TERMS = [
    "warning", "threat", "police", "court", "legal", "action", "penalty",
    "fine", "interest", "byaj", "jurmana", "darra", "dhamki", "fir",
    "urgent", "immediately", "turant bhugtan", "barbaad", "defaulter",
    "blacklist", "seize", "badnaam", "force", "otherwise", "warn",
]


class PoliteReminderService:
    """
    Generates and validates ethical, polite reminders for Kirana store customers.
    """

    @staticmethod
    def is_opted_in(customer: Customer) -> bool:
        """Verify whether customer has given consent for reminders."""
        return bool(customer.opted_in_reminders)

    @classmethod
    def validate_message_safety(cls, message: str) -> bool:
        """
        Safety check: Ensures zero pressure or coercive language exists.
        Returns True if safe, False if prohibited terms detected.
        """
        msg_lower = message.lower()
        for term in BANNED_PRESSURE_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', msg_lower):
                return False
        return True

    @classmethod
    def generate_polite_reminder(
        cls,
        customer: Customer,
        balance: float,
        language: str = "hi-IN",
        shop_name: str = "Aapki Apni Dukaan",
    ) -> Dict[str, Any]:
        """
        Generate a strictly compliant, courteous reminder notice.
        """
        # Guardrail 1: Check Opt-in
        if not cls.is_opted_in(customer):
            return {
                "success": False,
                "opted_in": False,
                "message": (
                    f"Reminder nahi bheja gaya: {customer.name} ne reminders ke liye opt-in nahi kiya hai. "
                    "DPDP Act aur Responsible AI niyam ke mutabiq bina sahmati ke reminder bhejna manaa hai."
                ),
                "spoken_text": (
                    f"{customer.name} ne opt-in nahi kiya hai. "
                    "Niyamanusaar bina sahmati reminder nahi bheja ja sakta."
                ),
            }

        # Guardrail 2: Ensure customer actually owes money
        if balance <= 0:
            return {
                "success": False,
                "opted_in": True,
                "message": f"{customer.name} ka koi baaki hisaab nahi hai.",
                "spoken_text": f"{customer.name} ka koi hisaab baaki nahi hai.",
            }

        amt_int = int(round(balance))

        # Polite templates without pressure or deadlines
        if language.startswith("hi"):
            sms_text = (
                f"Namaste {customer.name} ji,\n"
                f"{shop_name} ki taraf se shubhkaamnayein.\n"
                f"Aapka kul khata balance ₹{amt_int:,} hai.\n"
                f"Aap apni suvidha ke anusar aane par dekh lijiye ga. Shukriya!\n"
                f"- BolKhata AI Assistant"
            )
            spoken_text = (
                f"{customer.name} ji ke liye vinamra reminder taiyyar hai: "
                f"Aapka ₹{amt_int:,} ka hisaab hai, suvidhanusar dekh lijiye."
            )
        else:
            sms_text = (
                f"Hello {customer.name},\n"
                f"Warm greetings from {shop_name}.\n"
                f"This is a gentle update that your pending ledger balance is ₹{amt_int:,}.\n"
                f"Please review at your convenience whenever you visit next. Thank you!\n"
                f"- BolKhata AI"
            )
            spoken_text = (
                f"Polite reminder created for {customer.name}: "
                f"Pending balance ₹{amt_int:,}, review at convenience."
            )

        # Guardrail 3: Verify output safety
        assert cls.validate_message_safety(sms_text), "Generated reminder violated safety guardrails!"

        return {
            "success": True,
            "opted_in": True,
            "customer_id": customer.id,
            "customer_name": customer.name,
            "phone": customer.phone,
            "balance": balance,
            "reminder_text": sms_text,
            "spoken_text": spoken_text,
            "guardrail_status": "PASSED_RESPONSIBLE_AI_CHECK",
        }


reminder_service = PoliteReminderService()
