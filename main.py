import os
import requests
import csv
import io
import random
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Retrieve environment variables.
BACKEND_URL = os.getenv('BACKEND_URL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
WORKSPACE_UUID = os.getenv('WORKSPACE_UUID')

LOGIN_PATH = '/auth/login'
EXPORT_PATH = f'/ticket/export-pending/{WORKSPACE_UUID}'
IMPORT_PATH = '/ticket/import-statuses'

def create_app() -> FastAPI:
    """
    Creates and configures a simple FastAPI application.
    """
    app = FastAPI(
        title='Ticket CSV Automation',
        version='1.0.0',
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    return app

app = create_app()

def get_jwt_token():
    if not all([BACKEND_URL, USERNAME, PASSWORD]):
        raise ValueError('Environment variables BACKEND_URL, USERNAME, and PASSWORD must be set.')
    
    url = f'{BACKEND_URL}{LOGIN_PATH}'
    payload = {'email': USERNAME, 'password': PASSWORD}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f'Authentication failed: {e}')

def fetch_csv(token):
    if not WORKSPACE_UUID:
        raise ValueError('Environment variable WORKSPACE_UUID must be set.')

    url = f'{BACKEND_URL}{EXPORT_PATH}'
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        json_response: dict = response.json()
        csv_content = json_response.get('data')

        return csv_content if csv_content is not None else ''
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f'Failed to fetch CSV: {e}')
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f'Invalid response format from backend: {e}')

def update_csv(csv_content):
    input_csv = io.StringIO(csv_content)
    reader = csv.DictReader(input_csv)
    fieldnames = reader.fieldnames

    if not csv_content.strip() or not fieldnames:
        return ''

    output_csv = io.StringIO()
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        if row.get('status') == 'PENDING':
            rand = random.random()
            if rand < 0.3:
                new_status = 'PENDING'
            elif rand < 0.6:
                new_status = 'OPEN'
            else:
                new_status = 'CLOSED'
            row['status'] = new_status
        writer.writerow(row)

    return output_csv.getvalue()

def send_updated_csv(token, csv_content):
    url = f'{BACKEND_URL}{IMPORT_PATH}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {'csvContent': csv_content}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f'Failed to send updated CSV: {e}')

def run_automation():
    print('Authenticating...')
    token = get_jwt_token()

    print('Fetching Pending tickets CSV...')
    csv_content = fetch_csv(token)

    if not csv_content.strip():
        return {'message': 'No pending tickets to process.'}

    print('Processing CSV and updating statuses...')
    updated_csv = update_csv(csv_content)

    print('Sending updated CSV back to backend...')
    result = send_updated_csv(token, updated_csv)

    print('Update result:', result)
    return {'message': 'Automation process completed successfully.', 'result': result}

@app.post('/run-automation')
async def run_automation_endpoint():
    try:
        return run_automation()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'An unexpected error occurred: {e}')

@app.get("/health")
async def health_check():
    return {"status": "ok"}
