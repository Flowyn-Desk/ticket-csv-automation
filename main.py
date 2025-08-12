import os
import requests
import csv
import io
import random

BACKEND_URL = os.getenv('BACKEND_URL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

LOGIN_PATH = '/auth/login'
EXPORT_PATH = '/tickets/export-csv'
IMPORT_PATH = '/tickets/import-csv'

def get_jwt_token():
    url = f'{BACKEND_URL}{LOGIN_PATH}'
    payload = {'email': USERNAME, 'password': PASSWORD}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()['data']

def fetch_csv(token):
    url = f'{BACKEND_URL}{EXPORT_PATH}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def update_csv(csv_content):
    input_csv = io.StringIO(csv_content)
    reader = csv.DictReader(input_csv)
    fieldnames = reader.fieldnames

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
        'Content-Type': 'text/csv'
    }
    response = requests.post(url, data=csv_content, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    print('Authenticating...')
    token = get_jwt_token()

    print('Fetching Pending tickets CSV...')
    csv_content = fetch_csv(token)

    print('Processing CSV and updating statuses...')
    updated_csv = update_csv(csv_content)

    print('Sending updated CSV back to backend...')
    result = send_updated_csv(token, updated_csv)

    print('Update result:', result)

if __name__ == '__main__':
    main()
