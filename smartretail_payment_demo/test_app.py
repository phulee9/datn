import os
os.environ['PAYMENT_ACCOUNT']='0123456789'  # dummy test account
os.environ['PAYMENT_ACCOUNT_NAME']='TEST USER'
os.environ['PAYMENT_DEMO_MODE']='true'
from fastapi.testclient import TestClient
from app import app, PAYMENTS
client=TestClient(app)

def setup_function():
    PAYMENTS.clear()

def test_create_and_pending():
    r=client.post('/payments',json={'invoice_id':'000128','amount_vnd':285000})
    assert r.status_code==200
    d=r.json()
    assert d['status']=='PENDING'
    assert 'amount=285000' in d['qr_image_url']
    assert 'addInfo=SR000128' in d['qr_image_url']
    assert d['account_masked'].endswith('6789')

def test_idempotency_and_amount_conflict():
    payload={'invoice_id':'000128','amount_vnd':285000}
    assert client.post('/payments',json=payload).status_code==200
    assert client.post('/payments',json=payload).status_code==200
    assert client.post('/payments',json={**payload,'amount_vnd':1}).status_code==409

def test_simulation_never_marks_real_paid():
    client.post('/payments',json={'invoice_id':'2','amount_vnd':1000})
    result=client.post('/demo/payments/SR2/simulate-paid')
    assert result.json()['status']=='DEMO_PAID'

def test_invalid_amount():
    assert client.post('/payments',json={'invoice_id':'1','amount_vnd':0}).status_code==422
