import unittest
from loop_state import generate_reflection

class TestLoopState(unittest.TestCase):
    def test_generate_reflection(self):
        input_state = {"emotion": "sadness", "context": "loneliness"}
        result = generate_reflection(input_state)
        self.assertIsInstance(result, str)
        self.assertIn("loneliness", result.lower())

if __name__ == '__main__':
    unittest.main()
