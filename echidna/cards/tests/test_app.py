import os

from twisted.trial.unittest import TestCase


class TestApp(TestCase):
    """Run the simulate script since it does not work within the test
    environment process"""

    def test_simulate(self):
        #os.system('../ve/bin/python ../simulate.py')
        os.system('python ../simulate.py')
