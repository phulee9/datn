"""Local-only SmartRetail payment prototype. Never use as a production payment verifier."""
import os
import re
from io import BytesIO
from decimal import Decimal
from urllib.parse import quote
import qrcode
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

app = FastAPI(title="SmartRetail Payment Prototype", version="0.1")
BANK_BIN = os.getenv("PAYMENT_BANK_BIN", "970422")  # example MB Bank; verify before real use
ACCOUNT = os.getenv("PAYMENT_ACCOUNT", "")
ACCOUNT_NAME = os.getenv("PAYMENT_ACCOUNT_NAME", "")
PAYMENTS = {}  # in-memory demo only; replace with PostgreSQL transactions

class CreatePayment(BaseModel):
    invoice_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    amount_vnd: int = Field(gt=0, le=100_000_000)

@app.post('/payments')
def create_payment(body: CreatePayment):
    if not ACCOUNT or not ACCOUNT_NAME or not re.fullmatch(r"\d{6,25}", ACCOUNT):
        raise HTTPException(503, "Configure PAYMENT_ACCOUNT and PAYMENT_ACCOUNT_NAME first")
    payment_id = f"SR{body.invoice_id}".upper()
    if len(payment_id) > 50:
        raise HTTPException(400, "Payment reference too long")
    old = PAYMENTS.get(payment_id)
    if old:
        if old['amount_vnd'] != body.amount_vnd:
            raise HTTPException(409, "Existing payment amount cannot change")
        return old
    # VietQR public image endpoint; no API key. Use only after validating provider terms.
    url = (f"https://img.vietqr.io/image/{BANK_BIN}-{ACCOUNT}-compact2.png"
           f"?amount={body.amount_vnd}&addInfo={quote(payment_id)}&accountName={quote(ACCOUNT_NAME)}")
    record = {"payment_id": payment_id, "invoice_id": body.invoice_id,
              "amount_vnd": body.amount_vnd, "bank_bin": BANK_BIN,
              "account_name": ACCOUNT_NAME, "account_masked": '*' * max(0,len(ACCOUNT)-4)+ACCOUNT[-4:],
              "qr_image_url": url, "status": "PENDING"}
    PAYMENTS[payment_id] = record
    return record

@app.get('/payments/{payment_id}')
def get_payment(payment_id: str):
    record = PAYMENTS.get(payment_id)
    if not record:
        raise HTTPException(404, "Payment not found")
    return record

@app.post('/demo/payments/{payment_id}/simulate-paid')
def simulate_paid(payment_id: str):
    if os.getenv('PAYMENT_DEMO_MODE', 'false').lower() != 'true':
        raise HTTPException(404, "Demo endpoint disabled")
    record = PAYMENTS.get(payment_id)
    if not record:
        raise HTTPException(404, "Payment not found")
    record['status'] = 'DEMO_PAID'  # deliberately NOT PAID
    return record
