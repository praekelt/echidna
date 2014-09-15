import os

from twisted.trial.unittest import TestCase


class TestApp(TestCase):
    """Run the simulate script since it does not work within the test
    environment process"""

    def test_simulate(self):
        pth = '../ve/bin/python'
        os.system(
            (os.path.exists(pth) and pth or 'python') \
                + ' ../simulate.py'
        )
