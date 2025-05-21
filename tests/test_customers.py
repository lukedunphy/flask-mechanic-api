import unittest
from app import create_app
from app.models import db, Customer
from marshmallow import ValidationError


class TestCustomer(unittest.TestCase):
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
            db.session.add(customer)
            db.session.commit()
            self.customer_id = customer.id
        self.client = self.app.test_client()


    def test_customer_login(self):
        payload = {
            "email": "test@test.com",
            "password": "1234"
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "success")
        self.assertIn('token', response.json)


    def test_invalid_customer_login(self):
        payload = {
            "email": "wrongemail",
            "password": "wrongpassword"
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json['message'],
              "invalid email or password"
        )


    def test_get_customer(self):
        response = self.client.get(f'/customers/{self.customer_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], self.customer_id)
        self.assertEqual(response.json['name'], "Test")
        self.assertEqual(response.json['email'], "test@test.com")
        self.assertEqual(response.json['phone'], "1111111111")
        self.assertEqual(response.json['password'], "1234")


    def test_invalid_get_customer(self):
        response = self.client.get('customers/999')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "invalid customer id")


    def test_create_customer(self):
        payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "password": "1234",
            "phone": "1234567890"
        }

        response = self.client.post('/customers/', json=payload)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")


    def test_create_invalid_customer(self):
        payload = {
            "name": "John Doe",
            "password": "1234",
            "phone": "1234567890"
        }

        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)


    def test_get_customers(self):
        response = self.client.get('/customers/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], "Test")


    def test_update_customer(self):
        login = self.client.post(
            '/customers/login',
            json={"email": "test@test.com", "password": "1234"}
        )
        token = login.json['token']
        headers = {"Authorization": "Bearer " + token}

        payload = {
            "name":     "UpdatedName",
            "email":    "test@test.com",
            "password": "1234",
            "phone":    "1111111111"
        }
        response = self.client.put('/customers/', json=payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "UpdatedName")


    def test_update_customer_unauthorized(self):
        payload = {
            "name":     "NoAuth",
            "email":    "test@test.com",
            "password": "1234",
            "phone":    "1111111111"
        }

        response = self.client.put('/customers/', json=payload)

        self.assertEqual(response.status_code, 400)


    def test_delete_customer(self):
        login = self.client.post(
            '/customers/login',
            json={"email": "test@test.com", "password": "1234"}
        )
        token = login.json['token']
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.delete('/customers/', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['message'],
            f"successfully deleted customer {self.customer_id}"
        )


    def test_delete_customer_unauthorized(self):
        response = self.client.delete('/customers/')

        self.assertEqual(response.status_code, 400)


    def test_search_customer_found(self):
        response = self.client.get('/customers/search?email=test')
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['email'], "test@test.com")

    def test_search_customer_not_found(self):
        response = self.client.get('/customers/search?email=nomatch')
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json, [])