import os
import requests
import csv
import io
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Config from environment
BACKEND_URL = os.getenv('BACKEND_URL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
WORKSPACE_UUID = os.getenv('WORKSPACE_UUID')

if __name__ == '__main__':
    app = FastAPI(title='Ticket CSV Automation')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def get_token():
    url = f'{BACKEND_URL}/user/authenticate'
    resp = requests.post(url, json={'email': USERNAME, 'password': PASSWORD})
    resp.raise_for_status()
    return resp.json()['data']

def fetch_pending_csv(token):
    url = f'{BACKEND_URL}/ticket/export-pending/{WORKSPACE_UUID}'
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get('data', '')

def update_statuses(csv_content):
    input_csv = io.StringIO(csv_content)
    reader = csv.DictReader(input_csv)
    if not reader.fieldnames:
        return ''

    output_csv = io.StringIO()
    writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        if row.get('status') == 'PENDING':
            r = random.random()
            if r < 0.3:
                row['status'] = 'PENDING'
            elif r < 0.6:
                row['status'] = 'OPEN'
            else:
                row['status'] = 'CLOSED'
        writer.writerow(row)

    return output_csv.getvalue()

def send_updated_csv(token, csv_content):
    # Sends updated CSV back to backend
    url = f'{BACKEND_URL}/ticket/import-statuses'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {'csvContent': csv_content}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

@app.post('/run-automation')
def run_automation():
    # Runs the full automation process
    token = get_token()
    csv_content = fetch_pending_csv(token)
    if not csv_content.strip():
        return {'message': 'No pending tickets found.'}

    updated_csv = update_statuses(csv_content)
    result = send_updated_csv(token, updated_csv)
    return {'message': 'Automation complete', 'result': result}

@app.get('/health')
def health_check():
    return {'status': 'ok'}
