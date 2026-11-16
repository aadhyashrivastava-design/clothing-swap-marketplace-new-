import unittest
import json
from app import app
from database import init_db

class EcoSwapTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_homepage(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'EcoSwap', res.data)

    def test_current_user(self):
        res = self.client.get('/api/me')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['username'], 'mayalin')

    def test_items_marketplace(self):
        res = self.client.get('/api/items')
        self.assertEqual(res.status_code, 200)
        items = res.get_json()
        self.assertGreater(len(items), 0)
        self.assertIn('distance_miles', items[0])
        self.assertIn('barter_score', items[0])

    def test_fair_match(self):
        # Match Maya's wardrobe against item #4 (Carhartt Chore Coat)
        res = self.client.get('/api/fair-match/4')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('matches', data)
        self.assertGreater(len(data['matches']), 0)
        top_match = data['matches'][0]
        self.assertIn('fairness', top_match)
        self.assertGreaterEqual(top_match['fairness']['fairness_pct'], 50)

    def test_eco_impact(self):
        res = self.client.get('/api/eco-impact')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('platform', data)
        self.assertGreater(data['platform']['water_saved_l'], 1000)

if __name__ == '__main__':
    unittest.main()
