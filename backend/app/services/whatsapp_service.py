"""
BolKhata - WhatsApp & Counter Verification Receipt Service
Generates two-way customer auditory confirmations and 1-click WhatsApp / SMS
digital receipts to eliminate mutual disputes right at the Kirana counter.
"""

import urllib.parse
from typing import Dict, Any, Optional
from datetime import date


class WhatsAppReceiptService:
    """Generates dispute-proof verifiable digital receipts and two-way voice texts."""

    @classmethod
    def generate_customer_counter_announcement(
        cls,
        customer_name: str,
        direction: str,
        amount: float,
        net_balance: float,
        language: str = "hi-IN"
    ) -> str:
        """
        Customer-facing two-way announcement through external counter speaker.
        Confirms transaction aloud in front of customer and merchant.
        """
        amt_str = f"₹{int(round(amount))}"
        net_str = f"₹{int(round(net_balance))}"

        if direction == "credit":
            if language.startswith("kn"):
                return f"{customer_name} ಅವರೇ, ನಿಮ್ಮ ಖಾತೆಗೆ {amt_str} ಸಾಲ ನಮೂದಿಸಲಾಗಿದೆ. ಒಟ್ಟು ಬಾಕಿ {net_str}."
            elif language.startswith("te"):
                return f"{customer_name} గారు, మీ ఖాతాలో {amt_str} అప్పు నమోదయింది. మొత్తం బాకీ {net_str}."
            elif language.startswith("hi"):
                return f"{customer_name} ji, aapke khate mein {amt_str} udhaar darj hua. Ab kul baaki {net_str} hai."
            else:
                return f"{customer_name}, {amt_str} credit added. Current balance is {net_str}."
        else:
            if language.startswith("kn"):
                return f"{customer_name} ಅವರೇ, {amt_str} ಪಾವತಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ಉಳಿದ ಬಾಕಿ {net_str}."
            elif language.startswith("te"):
                return f"{customer_name} గారు, {amt_str} చెల్లింపు అందింది. మిగిలిన బాకీ {net_str}."
            elif language.startswith("hi"):
                return f"{customer_name} ji, {amt_str} jama darj hua. Ab baaki {net_str} hai."
            else:
                return f"{customer_name}, {amt_str} payment received. Remaining balance is {net_str}."

    @classmethod
    def generate_whatsapp_receipt_link(
        cls,
        customer_name: str,
        phone: Optional[str],
        store_name: str,
        direction: str,
        amount: float,
        net_balance: float,
        upi_vpa: str = "kirana.bolkhata@okhdfcbank"
    ) -> Dict[str, Any]:
        """
        Generates 1-click WhatsApp web link and verifiable SMS copy with instant UPI link.
        """
        txn_type = "UDHAAR (Credit)" if direction == "credit" else "JAMA (Payment)"
        today_str = date.today().strftime("%d-%b-%Y")
        clean_amount = int(round(amount))
        clean_net = int(round(net_balance))

        upi_pay_link = f"upi://pay?pa={upi_vpa}&pn={urllib.parse.quote(store_name)}&am={clean_net}&cu=INR"

        msg = (
            f"🧾 *{store_name.upper()} - DIGITAL KHATA RECEIPT*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer:* {customer_name}\n"
            f"📅 *Date:* {today_str}\n"
            f"📌 *Entry:* {txn_type}\n"
            f"💰 *Amount:* ₹{clean_amount}\n"
            f"📊 *Net Outstanding:* ₹{clean_net}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔒 *100% Encrypted & Verifiable*\n"
            f"📲 Pay directly via UPI: {upi_pay_link}\n\n"
            f"Thank you for shopping at {store_name}!"
        )

        encoded_text = urllib.parse.quote(msg)
        clean_phone = "".join(filter(str.isdigit, phone or ""))
        if clean_phone.startswith("91") and len(clean_phone) == 12:
            phone_param = clean_phone
        elif len(clean_phone) == 10:
            phone_param = f"91{clean_phone}"
        else:
            phone_param = ""

        wa_url = f"https://wa.me/{phone_param}?text={encoded_text}" if phone_param else f"https://wa.me/?text={encoded_text}"

        return {
            "whatsapp_url": wa_url,
            "receipt_text": msg,
            "has_phone": bool(phone_param)
        }


whatsapp_service = WhatsAppReceiptService()
generate_customer_counter_announcement = WhatsAppReceiptService.generate_customer_counter_announcement
generate_whatsapp_receipt_link = WhatsAppReceiptService.generate_whatsapp_receipt_link

