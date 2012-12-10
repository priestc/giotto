import unittest

from giotto.programs import GiottoProgram
from giotto.exceptions import MockNotFound

def model(x, y):
    return None

class ProgramTest(unittest.TestCase):

    def test_no_mock_found(self):
        """
        The program raises MockNotFound when the program has no mock defined
        """
        gp = GiottoProgram(model=[model])
        self.assertRaises(MockNotFound, lambda: gp.get_model_mock())

    def test_no_mock_needed(self):
        """
        The program raises MockNotFound when the program has no mock defined
        """
        gp = GiottoProgram(model=[])
        self.assertEquals({}, gp.get_model_mock())

    def test_mock_found(self):
        """
        The program raises MockNotFound when the program has no mock defined
        """
        gp = GiottoProgram(model=[model, {'mock': True}])
        self.assertEquals({'mock': True}, gp.get_model_mock())

if __name__ == '__main__':
    unittest.main()