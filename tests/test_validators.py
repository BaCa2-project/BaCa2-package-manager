import unittest
from pathlib import Path

import baca2PackageManager.validators as validators


class ValidatorsTest(unittest.TestCase):

    def test_func_validator(self):
        v1 = validators.ValidatorFunc(lambda x: 1 <= x < 3)
        self.assertTrue(v1(2))
        self.assertFalse(v1(10))
        v2 = validators.ValidatorFunc(lambda x: x > 5, assert_type=int)
        self.assertTrue(v2.validate(6))
        self.assertFalse(v2.validate(6.))

        @validators.ValidatorFunc.decorate(int)
        def v3(x):
            return x > 5

        self.assertTrue(v3.validate(6))
        self.assertFalse(v3.validate(6.))

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
        v = validators.ValidatorSeries(validators.ValidatorSeries.Operator.OR, v_list)
        self.assertTrue(v(1))
        v = validators.ValidatorSeries(validators.ValidatorSeries.Operator.AND, v_list)
        self.assertFalse(v(1))
        self.assertTrue(v(1.))

    def test_isin_validator(self):
        v = validators.IsIn([1, 2, 3, 4])
        self.assertTrue(v.validate(1))
        self.assertFalse(v.validate(5))

    def test_isnone(self):
        v = validators.IsNone()
        self.assertTrue(v.validate(None))
        self.assertFalse(v.validate('None'))

    def test_is_not_empty(self):
        v = validators.IsNotEmpty()
        self.assertTrue(v.validate('a'))
        self.assertFalse(v.validate(''))

    def test_istype(self):
        v = validators.IsType((int, float))
        self.assertTrue(v.validate(1))
        self.assertTrue(v.validate(1.2))
        self.assertFalse(v.validate('1.1'))

    def test_is_exactly(self):
        v = validators.IsExactly('42')
        self.assertTrue(v.validate('42'))
        self.assertFalse(v.validate(42))

    def test_is_regex_match(self):
        v = validators.IsRegexMatch(r'[A-Za-z.]+@[A-Za-z]{2,}\.(com|pl|org)')
        self.assertTrue(v.validate('grzegorz.brzeczyszczykiewicz@gmail.com'))
        self.assertFalse(v.validate('wrong_email@gmial.com'))

    def test_is_alphanumeric(self):
        v = validators.IsAlphanumeric()
        self.assertTrue(v.validate('1234frfrnocap'))
        self.assertFalse(v.validate('not. alpha. numeric.'))

    def test_is_path(self):
        v = validators.IsPath()
        self.assertTrue(v.validate('/usr/bin'))  # Do not use Windows (bad practice)
        self.assertFalse(v.validate('/does/not/exist'))
        self.assertTrue(v.validate(Path('/usr/bin')))

    def test_is_restricted_list(self):
        v = validators.IsRestrictedList(validators.IsType(str))
        self.assertTrue(v.validate(['a', 'b', 'c']))
        self.assertFalse(v.validate(['a', 'b', 2]))


if __name__ == '__main__':
    unittest.main()
