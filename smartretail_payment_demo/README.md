# SmartRetail Payment Module — local prototype

This prototype creates a **real VietQR payment request image URL** targeting the bank account configured on the backend, but it **does not verify real transfers**. Do not deploy as a production payment system. It uses in-memory state, has no authentication, and the demo endpoint is intentionally unsafe outside localhost.

## Setup (Python 3.10+)

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Set environment variables (Windows PowerShell example):

```powershell
$env:PAYMENT_BANK_BIN="970422"
$env:PAYMENT_ACCOUNT="YOUR_REAL_BANK_ACCOUNT"
$env:PAYMENT_ACCOUNT_NAME="YOUR_ACCOUNT_HOLDER_NAME"
$env:PAYMENT_DEMO_MODE="true"
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000/docs. POST `/payments` with `{ "invoice_id": "000128", "amount_vnd": 285000 }`. Response contains `qr_image_url`; open it to see QR. GET `/payments/SR000128` returns `PENDING`. POST `/demo/payments/SR000128/simulate-paid` changes it to `DEMO_PAID` **only**, not a verified real payment.

Run `pytest -q` to check idempotency, amount, and state handling.

## Next steps before real money automation

1. Replace in-memory records with PostgreSQL, unique payment reference and immutable amount.
2. Compute amounts from finalized server-side invoice items, never accept a client-supplied total.
3. Obtain a bank/payment-provider integration officially supporting account incoming transaction events. Confirm eligibility, fees, webhook signing, settlement and account restrictions.
4. Verify webhook authenticity and match destination account, amount, payment reference, provider transaction ID, and status. Enforce idempotency and replay protection; record audit logs.
5. Never treat frontend redirect, a screenshot, QR generation or a demo button as proof of payment.
6. Use a controlled HTTPS callback endpoint, access control, and proper secrets management; only verified payments become `PAID`.
7. Test with a small real transfer and confirm receipt in the bank app independently before enabling receipt printing.

Note: `img.vietqr.io` is a third-party QR image generator; it is not a payment confirmation service. The QR itself can be modified in the bank app before sending; never promise an absolute guarantee of recipient or amount solely from a QR.
