import os


class TestApp(TestCase):
    """Run the simulate script since it does not work within the test
    environment process"""

    def test_simulate(self):
        os.system('python simulate.py')
