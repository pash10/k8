import unittest

import yaml
from app import app
from dym_form import current_values, load_example


class EditorTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as session:
            token = session["csrf_token"]
        self.fields = {**current_values(load_example()), "csrf_token": token}

    def test_valid_download(self):
        response = self.client.post("/", data={**self.fields, "replicas": "4"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(yaml.safe_load(response.data)["spec"]["replicas"], 4)

    def test_csrf(self):
        self.assertEqual(self.client.post("/", data={**self.fields, "csrf_token": "wrong"}).status_code, 403)

    def test_reject_invalid_port(self):
        self.assertEqual(self.client.post("/", data={**self.fields, "port": "65536"}).status_code, 400)

    def test_reject_template_payload(self):
        self.assertEqual(self.client.post("/", data={**self.fields, "name": "{{7*7}}"}).status_code, 400)

    def test_reject_extra_field(self):
        self.assertEqual(self.client.post("/", data={**self.fields, "unexpected": "yes"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
