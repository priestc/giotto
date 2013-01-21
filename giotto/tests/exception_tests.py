import unittest

from giotto.exceptions import InvalidInput

class InvalidInputTest(unittest.TestCase):

    def test_just_message(self):
        exc1 = InvalidInput("Message")
        exc2 = InvalidInput(message="Message")

        self.assertEquals(exc1.message, "Message")
        self.assertEquals(str(exc1), "Message")
        self.assertEquals(str(exc1), str(exc2))

    def test_basic_kwargs(self):
        exc = InvalidInput("Message", x=3, y=2)
        self.assertEquals(exc.x['message'], '')
        self.assertEquals(exc.x['value'], 3)

    def test_complex_kwargs(self):
        exc = InvalidInput("Message", x={'message': "too large", "value": 4})
        self.assertEquals(exc.x['message'], "too large")
        self.assertEquals(exc.x['value'], 4)
        self.assertEquals(str(exc), "Message")

    def test_empty_template_safe(self):
        """
        Undefined vars on the exception are treated as empty vars
        """
        exc = InvalidInput("Message", x={'message': "too large", "value": 4})
        self.assertEquals([], [x for x in exc['y']])
        
    def test_direct_value_set(self):
        """
        Directly setting exception values works
        """
        exc = InvalidInput()
        exc.x = 4
        self.assertEquals(exc.x['value'], 4)
        self.assertEquals(exc.x['message'], '')

if __name__ == '__main__':
    unittest.main()