import csv
import io
from typing import Dict, List
from app.csv_automation import CsvAutomation
import unittest


class TestCsvAutomation(unittest.TestCase):

    def test_simulate_iteration_must_return_a_valida_csv_with_three_equal_parts(self) -> None:
        api_csv_content: str = ''
        with open('tests/csv_example.txt') as file:
            api_csv_content = file.read()
        csv_automation: CsvAutomation = CsvAutomation()
        result: str = csv_automation.simulate_iteration(api_csv_content)
        input_csv = io.StringIO(result)
        reader = csv.DictReader(input_csv)
        rows: List[Dict] = list(reader)
        total_lines: int = len(rows)
        pending_count: int = 0
        open_count: int = 0
        closed_count: int = 0
        other_count: int = 0
        for row in rows:
            status: str = row.get('status')
            match status:
                case 'PENDING':
                    pending_count += 1
                case 'OPEN':
                    open_count += 1
                case 'CLOSED':
                    closed_count += 1
                case _: 
                    other_count += 1
        self.assertIsNotNone(result)
        self.assertEqual(10, total_lines)
        self.assertEqual(3, pending_count)
        self.assertEqual(4, open_count)
        self.assertEqual(3, closed_count)
        self.assertEqual(0, other_count)        
