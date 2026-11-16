import unittest
import json
from app import app
from database import init_db

class EcoSwapIndiaTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_homepage(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'EcoSwap', res.data)

    def test_login_and_me(self):
        # Test Login with demo account
        login_res = self.client.post('/api/login', json={
            'email': 'priya@gmail.com',
            'password': '123'
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['name'], 'Priya Sharma')

        # Check /api/me
        me_res = self.client.get('/api/me')
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data['logged_in'])
        self.assertEqual(me_data['user']['city'], 'Bangalore')

    def test_items_in_rupees(self):
        res = self.client.get('/api/items')
        self.assertEqual(res.status_code, 200)
        items = res.get_json()
        self.assertGreater(len(items), 0)
        self.assertIn('price_inr', items[0])
        self.assertGreaterEqual(items[0]['price_inr'], 100)

    def test_fair_match_inr(self):
        # Login first as Priya
        self.client.post('/api/login', json={'email': 'priya@gmail.com', 'password': '123'})
        # Compare with item #4 (H&M Denim jacket, ₹1999)
        res = self.client.get('/api/fair-match/4')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('matches', data)
        self.assertGreater(len(data['matches']), 0)
        top = data['matches'][0]
        self.assertIn('comparison', top)
        self.assertIn('difference_inr', top['comparison'])

if __name__ == '__main__':
    unittest.main()
