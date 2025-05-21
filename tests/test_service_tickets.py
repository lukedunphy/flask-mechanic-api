import unittest
from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic, Inventory


class TestServiceTicket(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            customer = Customer(
                name="Test",
                email="test@test.com",
                password="1234",
                phone="1111111111"
            )
            mechanic1 = Mechanic(
                name="Test",
                email="test@test.com",
                salary=100000.00,
                password=('password1')
            )
            mechanic2 = Mechanic(
                name="Test2",
                email="test2@test.com",
                salary=1000000.00,
                password=('password2')
            )
            inventory = Inventory(
                name="Engine Filter",
                price=15.99
            )

            db.session.add(customer)
            db.session.add(mechanic1)
            db.session.add(mechanic2)
            db.session.add(inventory)
            db.session.commit()
            self.customer_id = customer.id
            self.mechanic1_id = mechanic1.id
            self.mechanic2_id = mechanic2.id
            self.inventory_id = inventory.id

        self.client = self.app.test_client()

    
    def test_create_ticket(self):
        payload = {
            "VIN": "1HGCM82633A004352",
            "service_date": "2025-05-14",
            "service_desc": "Oil change",
            "customer_id": self.customer_id,
            "mechanic_ids": [self.mechanic1_id, self.mechanic2_id]
        }
        response = self.client.post('/service-tickets/', json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], payload['VIN'])
        self.assertEqual(response.json['service_desc'], payload['service_desc'])
        self.assertEqual(response.json['service_date'], payload['service_date'])
        self.assertIn('id', response.json)


    def test_invalid_mechanic_ticket(self):
        payload = {
            "VIN": "1HGCM82633A004352",
            "service_date": "2025-05-14",
            "service_desc": "Oil change",
            "customer_id": self.customer_id,
            "mechanic_ids": [999]
        }
        response = self.client.post('/service-tickets/', json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "invalid mechanic id")
        

    def test_read_ticekt(self):
        payload = {
            "VIN":           "1HGCM82633A004352",
            "service_date":  "2025-05-14",
            "service_desc":  "Oil change",
            "customer_id":   self.customer_id,
            "mechanic_ids":  [self.mechanic1_id, self.mechanic2_id]
        }
        create_response = self.client.post('/service-tickets/', json=payload)

        self.assertEqual(create_response.status_code, 201)

        response = self.client.get('/service-tickets/')

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        first = response.json[0]
        self.assertEqual(first['VIN'], payload['VIN'])


    def test_invalid_read_ticket(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json, [])


    def test_edit_service_ticket(self):
        payload = {
            "VIN":           "1HGCM82633A004352",
            "service_date":  "2025-05-14",
            "service_desc":  "Oil change",
            "customer_id":   self.customer_id,
            "mechanic_ids":  [self.mechanic1_id]
        }
        resp1 = self.client.post('/service-tickets/', json=payload)
        self.assertEqual(resp1.status_code, 201)
        ticket_id = resp1.json['id']

        edit_payload = {"add_ids": [self.mechanic2_id], "remove_ids": []}
        resp2 = self.client.put(f'/service-tickets/{ticket_id}/edit', json=edit_payload)
        self.assertEqual(resp2.status_code, 200)

        ids = [m["id"] for m in resp2.json["mechanics"]]

        self.assertEqual(len(ids), 2)
        self.assertIn(self.mechanic1_id, ids)
        self.assertIn(self.mechanic2_id, ids)


    def test_edit_ticket_not_found(self):
        response = self.client.put('/service-tickets/999/edit', json={"add_ids":[], "remove_ids":[]})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "service ticket not found")


    def test_delete_service_ticket(self):
        payload = {
            "VIN":           "1HGCM82633A004352",
            "service_date":  "2025-05-14",
            "service_desc":  "Oil change",
            "customer_id":   self.customer_id,
            "mechanic_ids":  [self.mechanic1_id]
        }
        create_resp = self.client.post('/service-tickets/', json=payload)
        self.assertEqual(create_resp.status_code, 201)
        ticket_id = create_resp.json['id']

        delete_resp = self.client.delete(f'/service-tickets/{ticket_id}')
        self.assertEqual(delete_resp.status_code, 200)

        expected = f"Service ticket {ticket_id} deleted"
        self.assertEqual(delete_resp.json['message'], expected)


    def test_delete_ticket_not_found(self):
        response = self.client.delete('/service-tickets/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "service ticket not found")


    def test_add_part_to_ticket(self):
        ticket_payload = {
            "VIN":           "1HGCM82633A004352",
            "service_date":  "2025-05-14",
            "service_desc":  "Oil change",
            "customer_id":   self.customer_id,
            "mechanic_ids":  [self.mechanic1_id]
        }
        create_resp = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(create_resp.status_code, 201)
        ticket_id = create_resp.json['id']

        part_payload = {"part_id": self.inventory_id, "quantity": 2}
        resp = self.client.post(f'/service-tickets/{ticket_id}/parts', json=part_payload)
        self.assertEqual(resp.status_code, 200)

        ticket_parts = resp.json['ticket_parts']
        self.assertIsInstance(ticket_parts, list)
        self.assertEqual(ticket_parts[0]['part_id'], self.inventory_id)
        self.assertEqual(ticket_parts[0]['quantity'], 2)


    def test_add_part_invalid_ticket(self):
        payload = {
            "part_id": self.inventory_id,
            "quantity": 2
        }
        response = self.client.post('/service-tickets/999/parts', json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "invalid ticket id")


    def test_add_invalid_part(self):
        ticket_payload = {
            "VIN":           "1HGCM82633A004352",
            "service_date":  "2025-05-14",
            "service_desc":  "Oil change",
            "customer_id":   self.customer_id,
            "mechanic_ids":  [self.mechanic1_id]
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['id']

        part_payload = {
            "part_id": 999,
            "quantity": 2
        }
        response = self.client.post(f'service-tickets/{ticket_id}/parts', json=part_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "invalid part id")