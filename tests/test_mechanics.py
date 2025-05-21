import unittest
from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_token
from werkzeug.security import generate_password_hash


class TestMechanic(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name="Test",
            email="test@test.com",
            salary=100000.00,
            password=('123')
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()


    def test_login_mechanic(self):
        payload = {
            "email": "test@test.com",
            "password": "123"
        }

        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)


    def test_invalid_mechanic_login(self):
        payload = {
            "email": "test@test.com",
            "password": "wrongpassword"
        }

        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 401)
        text = response.get_data(as_text=True)
        self.assertIn("invalid email or password", text)



    def test_create_mechanic(self):
        payload = {
            "name": "Test2",
            "email": "test2@test.com",
            "password": "123",
            "salary": 50000.00
        }
        #send request
        response = self.client.post('/mechanics/', json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], payload['name'])
        self.assertEqual(response.json['email'], payload['email'])
        self.assertIn('id', response.json)


    def test_invalid_create_mechanic(self):
        payload = {
            "name": "Test2",
            "email": "test2@test.com",
            "password": "123"
        }
        response = self.client.post('/mechanics/', json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn('salary', response.json)


    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json),1)
        
        mechanic = response.json[0]
        self.assertEqual(mechanic['email'], "test@test.com")
        self.assertEqual(mechanic['name'], "Test")
        self.assertEqual(mechanic['salary'], 100000.00)
        self.assertIn('id', mechanic)


    def test_mechanic_update(self):
        update_payload = {
            "name": "NEW MECHANIC",
            "email": "test@test.com",
            "salary": 10000000.00,
            "password": "123"
        }

        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'NEW MECHANIC')


    def test_update_unauthorized(self):
        response = self.client.put('/mechanics/', json={"name": "X"})
        self.assertEqual(response.status_code, 400)


    def test_delete_mechanic(self):
        headers = {"Authorization": "Bearer " + self.token}
        
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['message'],
            f"successfully deleted mechanic 1"
        )


    def test_delete_unauthorized(self):
        response = self.client.delete('/mechanics/')
        self.assertEqual(response.status_code, 400)


    def test_popular_mechanic(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json[0]['email'], "test@test.com")