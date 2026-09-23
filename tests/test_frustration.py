import unittest
import numpy as np
from engine.core import CyberneticGovernor
from math import isclose

class TestFrustration(unittest.TestCase):
    def test_frustration_random_matrix(self):
        # A random matrix should have a frustration near 0.5
        np.random.seed(42)
        matrix = np.random.randn(23, 768).astype(np.float32)
        frust = CyberneticGovernor._calculate_coordinate_frustration(matrix)
        self.assertTrue(0.4 < frust < 0.6)
        
    def test_frustration_empty(self):
        matrix = np.random.randn(2, 768).astype(np.float32)
        frust = CyberneticGovernor._calculate_coordinate_frustration(matrix)
        self.assertEqual(frust, 0.0)

if __name__ == '__main__':
    unittest.main()
