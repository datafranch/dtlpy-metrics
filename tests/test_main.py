import os
import unittest
import dtlpy as dl

from dtlpymetrics.scoring import scorer


class TestRunner(unittest.TestCase):
    def setUp(self):
        dl.setenv("rc")
        print(f'env -> {dl.environment()}')
        email = os.environ.get('LOGIN_EMAIL', None)
        password = os.environ.get('LOGIN_EMAIL_PASSWORD', None)
        print(f'email {email}')
        if email and password:
            is_logged_in = dl.login_m2m(email, password)
            print(f'is_logged_in {is_logged_in}')
        else:
            dl.login()
        self.scorer = scorer
        self.item = dl.items.get(item_id='63d7adf427034d7bb3c7e673')

    def test_create_attribute_file(self):
        faces = self.scorer(item=self.item)
        print(f'faces -> {faces}')
        self.assertIsInstance(faces, dl.Item)


if __name__ == "__main__":
    unittest.main()
