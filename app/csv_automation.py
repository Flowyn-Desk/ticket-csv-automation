import csv
from http import HTTPStatus
import io
import math
import os
from typing import Dict
from fastapi.responses import JSONResponse
import requests


class CsvAutomation:

    def __init__(self):
        self.backend_url = os.getenv('BACKEND_URL')
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.workspace_uuid = os.getenv('WORKSPACE_UUID')
        self.manager_uuid = os.getenv('MANAGER_UUID')
    
    def __get_token(self) -> str:
        url = f'{self.backend_url}/user/authenticate'
        resp = requests.post(url, json={'email': self.username, 'password': self.password})
        resp.raise_for_status()
        return resp.json()['data']

    def __fetch_pending_csv(self, token: str) -> str:
        url = f'{self.backend_url}/ticket/export-pending/{self.workspace_uuid}'
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.post(url, headers=headers)
        resp.raise_for_status()
        return resp.json().get('data', '')

    def __import_csv(self, token: str, csv_content: str):
        url = f'{self.backend_url}/ticket/import-statuses'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {'csvContent': csv_content, 'managerUuid': self.manager_uuid}
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def simulate_iteration(self, csv_content: str) -> str:
        input_csv = io.StringIO(csv_content)
        reader = csv.DictReader(input_csv)
        rows = list(reader)
        total_lines = len(rows)
        pending_count = math.floor(total_lines * 0.33)
        closed_count = math.floor(total_lines * 0.33)
        output_rows = []
        for i, row in enumerate(rows):
            new_row = row.copy()
            if i < pending_count:
                new_row['status'] = 'PENDING'
            elif i < pending_count + closed_count:
                new_row['status'] = 'CLOSED'
            else:
                new_row['status'] = 'OPEN'
            output_rows.append(new_row)
        output_csv = io.StringIO()
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(output_csv, fieldnames=fieldnames, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(output_rows)
        return output_csv.getvalue()
    
    def simulate_external_service_provider_iteration(self, csv_content: str) -> JSONResponse:
        try:
            after_iteraction_csv_content: str = self.simulate_iteration(csv_content)
            content: Dict[str, str] = {
                'data': after_iteraction_csv_content,
                'message': 'The automation was successfully executed'
            }
            print('External support simulation finished successfully')
            return JSONResponse(content=content, status_code=HTTPStatus.OK)
        except Exception as ex:
            print(ex)
            content: Dict[str, str] = {
                'data': '',
                'message': 'Fail while executing simulation'
            }
            return JSONResponse(content=content, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        
    def run_automation(self) -> JSONResponse:
        try:
            token: str = self.__get_token()
            print('The token was provided')
            pending_csv_content: str = self.__fetch_pending_csv(token)
            print('Fetched pending tickets')
            after_iteraction_csv_content: str = self.simulate_iteration(pending_csv_content)
            print('Simulated interaction')
            self.__import_csv(token, after_iteraction_csv_content)
            print('Imported interaction')
            content: Dict[str, str] = {
                'data': after_iteraction_csv_content,
                'message': 'The automation was successfully executed'
            }
            print('Automation finished successfully')
            return JSONResponse(content=content, status_code=HTTPStatus.OK)
        except Exception as ex:
            print(ex)
            content: Dict[str, str] = {
                'data': '',
                'message': 'Fail while executing automation'
            }
            return JSONResponse(content=content, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)