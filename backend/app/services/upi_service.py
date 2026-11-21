"""
BolKhata - Conversational Voice-to-UPI Service
Generates dynamic BharatPe/BHIM/PhonePe/GPay compliant UPI payment requests
and counter display QR codes directly from voice commands.
"""

import urllib.parse
from typing import Dict, Any, Optional


class UPIService:
    """Handles dynamic UPI payment generation and soundbox settlement."""

    DEFAULT_VPA = "kirana.bolkhata@okhdfcbank"

    @classmethod
    def generate_upi_payload(
        cls,
        customer_name: str,
        amount: float,
        store_name: str,
        merchant_vpa: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a standardized dynamic UPI payment deep link and QR parameters."""
        vpa = merchant_vpa or cls.DEFAULT_VPA
        clean_amount = round(float(amount), 2)
        note = f"Kirana Khata Settlement - {customer_name}"

        # Standard NPCI UPI URI Specification
        params = {
            "pa": vpa,
            "pn": store_name,
            "am": f"{clean_amount:.2f}",
            "cu": "INR",
            "tn": note
        }
        upi_string = f"upi://pay?{urllib.parse.urlencode(params)}"

        # Generate direct QR code data URL using SVG or public QR image renderer
        encoded_upi = urllib.parse.quote(upi_string)
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={encoded_upi}"

        return {
            "success": True,
            "customer_name": customer_name,
            "amount": clean_amount,
            "store_name": store_name,
            "merchant_vpa": vpa,
            "upi_uri": upi_string,
            "qr_image_url": qr_image_url,
            "soundbox_announcement": f"₹{int(clean_amount)} praapt hue. {customer_name} ka hisaab clear."
        }


upi_service = UPIService()
generate_upi_payload = UPIService.generate_upi_payload

