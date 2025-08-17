from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from http import HTTPStatus
import os

from fastapi.responses import JSONResponse
from app.csv_automation import CsvAutomation


BACKEND_URL = os.getenv('BACKEND_URL')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
WORKSPACE_UUID = os.getenv('WORKSPACE_UUID')

app = FastAPI(title='Ticket CSV Automation')
csv_automation = CsvAutomation()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post('/simulate-external-support')
async def simulate_external_support(request: Request):
    print('Running external support simulation')
    body: Dict = await request.json()
    csv_content: str = body.get('csvContent')
    return csv_automation.simulate_external_service_provider_iteration(csv_content)

@app.post('/run-automation')
async def run_automation(request: Request):
    print('Running automation')
    body: Dict = await request.json()
    csv_content: str = body.get('csvContent')
    return csv_automation.run_automation(csv_content)

@app.get('/health')
def health_check():
    return JSONResponse(content={}, status_code=HTTPStatus.OK)
