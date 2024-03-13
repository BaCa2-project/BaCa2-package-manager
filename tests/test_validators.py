import unittest

import baca2PackageManager.validators as validators


class ValidatorsTest(unittest.TestCase):

    def test_func_validator(self):
        v1 = validators.ValidatorFunc(lambda x: 1 <= x < 3)
        self.assertTrue(v1(2))
        self.assertFalse(v1(10))

    def test_validator_not(self):
        v1 = validators.ValidatorFunc(lambda x: 1 <= x < 3)
        vn = validators.ValidatorNot(v1)
        self.assertFalse(vn(2))
        self.assertTrue(vn(10))

    def test_validator_series(self):
        v_list = [
            validators.ValidatorFunc(lambda x: isinstance(x, float)),
            validators.ValidatorFunc(lambda x: x == 1)
        ]
        v = validators.ValidatorSeries(any, v_list)
        self.assertTrue(v(1))
        v = validators.ValidatorSeries(all, v_list)
        self.assertFalse((v(1)))
        self.assertTrue((v(1.)))


if __name__ == '__main__':
    unittest.main()
