import unittest
import json
from datetime import datetime, timedelta
import requests

class TestTimezoneAPI(unittest.TestCase):
    base_url = 'http://localhost:6666'

    def test_get_request_handler(self):
        response = requests.get(f'{self.base_url}/Europe/Moscow')
        self.assertEqual(response.status_code, 200)
        # Проверяем, что ответ содержит текущее время в правильном формате
        current_time_str = datetime.now(tz=response.headers['Date']).strftime('%Y-%m-%d %H:%M:%S %Z')
        self.assertIn(current_time_str, response.text)

    def test_post_convert_handler(self):
        data = {
            'date': '12.31.2023 15:30:00',
            'tz': 'Europe/Moscow'
        }
        response = requests.post(f'{self.base_url}/api/v1/convert/America/New_York', json=data)
        self.assertEqual(response.status_code, 200)
        converted_time = datetime.strptime(json.loads(response.text), '%Y-%m-%d %H:%M:%S %Z')
        expected_time = datetime(2023, 12, 31, 9, 30, tzinfo=converted_time.tzinfo)  # Предполагаемый результат
        self.assertEqual(converted_time, expected_time)

    def test_post_datediff_handler(self):
        data = {
            'first_date': '31.12.2023 15:30:00',
            'first_tz': 'Europe/Moscow',
            'second_date': '03:00PM 2023-12-31',
            'second_tz': 'America/New_York'
        }
        response = requests.post(f'{self.base_url}/api/v1/datediff', json=data)
        self.assertEqual(response.status_code, 200)
        time_diff_seconds = float(response.text)
        expected_diff_seconds = timedelta(hours=8).total_seconds()  # Предполагаемый результат
        self.assertAlmostEqual(time_diff_seconds, expected_diff_seconds, delta=1)

if __name__ == '__main__':
    unittest.main()

