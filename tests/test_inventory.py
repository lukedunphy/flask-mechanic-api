import unittest
from app import create_app
from app.models import db, Inventory
from app.utils.util import encode_token


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            inventory = Inventory(name="Engine Filter", price=15.99)
            db.session.add(inventory)
            db.session.commit()
            self.item_id = inventory.id
        self.client = self.app.test_client()


    def test_create_inventory(self):
        payload = {
            "name": "Cabin Filter",
            "price": 10.99
        }

        response = self.client.post('/inventory/', json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], payload['name'])
        self.assertEqual(response.json['price'], payload['price'])
        self.assertIn('id', response.json)


    def test_invalid_create_inventory(self):
        payload = {
            "name": "Cabin Filter"
        }

        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json)
        

    def test_update_inventory(self):
        payload = {
            "name": "Updated Name",
            "price": 20.99
        }
        response = self.client.put(f'/inventory/{self.item_id}', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], payload['name'])
        self.assertEqual(response.json['price'], payload['price'])


    def test_update_inventory_not_found(self):
        payload = {
            "name":  "DoesNotExist",
            "price": 5.55
        }

        response = self.client.put('/inventory/999', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "invalid id")


    def test_update_inventory_invalid_payload(self):
        payload = {"name": "OnlyName"}
        response = self.client.put(f'/inventory/{self.item_id}', json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json)


    def test_delete_inventory(self):
        response = self.client.delete(f'/inventory/{self.item_id}')


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], f'successfully deleted inventory item {self.item_id}')


    def test_invalid_delete_inventory(self):
        response = self.client.delete('/inventory/999')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "invalid id")