import shutil
from unittest import TestCase

from parameterized import parameterized
import pytest

from baca2PackageManager.manager_exceptions import NoSetFound, NoTestFound, InvalidFileExtension
from baca2PackageManager.validators import isAny, isNone, isInt, isIntBetween, isFloat, \
    isFloatBetween, isStr, is_, \
    isIn, isShorter, isDict, isPath, isSize, isList, valid_memory_size, \
    hasStructure, isSize
from baca2PackageManager.tools import bytes_from_str
from baca2PackageManager import TestF as TF, TSet, Package, set_base_dir, base_dir, \
    add_supported_extensions
from pathlib import Path
from yaml import safe_load
import random
import string

add_supported_extensions('cpp')
set_base_dir(Path(__file__).parent / 'test_packages')


def generate_rand_int():
    return random.randint(0, 10000000)


def compare_memory_unit(unit1, unit2):
    units = ['B', 'K', 'M', 'G']
    try:
        index1 = units.index(unit1)
        index2 = units.index(unit2)
        return index1 <= index2
    except ValueError:
        return False


def generate_rand_dict():
    _dict = {}
    for i in range(100):
        key1 = random.choice(string.ascii_letters)
        value1 = random.randint(1, 10000)
        key2 = random.randint(1, 10000)
        value2 = random.choice(string.ascii_letters)
        if i % 4 == 0:
            _dict[key1] = value1
        elif i % 4 == 1:
            _dict[key2] = value2
        elif i % 4 == 2:
            _dict[key1] = value2
        else:
            _dict[key2] = value1
    return _dict


def generate_rand_list():
    _list = []
    for i in range(100):
        val1 = random.choice(string.ascii_letters)
        val2 = random.randint(1, 10000)
        val3 = random.uniform(1, 10000)
        _list.append(val1)
        _list.append(val2)
        _list.append(val3)
    return list


class ValidationsTests(TestCase):

    def test_isInt(self):
        """
        It tests if the function isInt() works correctly
        """
        for i in range(1000):
            a = generate_rand_int()
            self.assertTrue(isInt(a))
            float(a)
            self.assertTrue(isInt(a))
            str(a)
            self.assertTrue(isInt(a))

        self.assertFalse(isInt(0.5))
        self.assertFalse(isInt('0.5'))
        self.assertFalse(isInt(1235.4567))
        self.assertFalse(isInt('1235.4567'))
        self.assertFalse(isInt('5,5'))
        self.assertFalse(isInt("5 and more"))
        self.assertFalse(isInt("It is just a string"))

    def test_isIntBetween(self):  # a <= val < b
        """
        It tests if the function is_IntBetween() works correctly        """
        for i in range(1000):
            a = generate_rand_int()
            b = generate_rand_int()
            if a > b:
                a, b = b, a
            val = random.randint(a, b - 1)
            self.assertTrue(isIntBetween(val, a, b))
            float(a)
            float(b)
            float(val)
            self.assertTrue(isIntBetween(val, a, b))
            val = random.randint(0, a - 1)
            self.assertFalse(isIntBetween(val, a, b))
            val = random.randint(b + 1, 10000001)
            self.assertFalse(isIntBetween(val, a, b))
        self.assertTrue(isIntBetween(5, 2, 10))
        self.assertTrue(isIntBetween(68, 68, 78))
        self.assertTrue(isIntBetween(-4, -7, -1))
        self.assertTrue(isIntBetween(-6, -6, 0))
        self.assertFalse(isIntBetween(5, 1, 3))
        self.assertFalse(isIntBetween(5, -7, -1))
        self.assertFalse(isIntBetween(5, -6, 0))
        self.assertFalse(isIntBetween(5, 6, 67))
        self.assertFalse(isIntBetween(67, 6, 67))

    def test_isFloat(self):
        """
        It tests if the function isFloat() works correctly
        """
        for i in range(1000):
            a = random.uniform(0.1, 100000.0)
            self.assertTrue(isFloat(a))
            float(a)
            self.assertTrue(isFloat(a))
            str(a)
            self.assertTrue(isFloat(a))
            a = random.random()
            self.assertTrue(isFloat(a))
            float(a)
            self.assertTrue(isFloat(a))
            str(a)
            self.assertTrue(isFloat(a))
        self.assertTrue(isFloat('5'))
        self.assertTrue(isFloat(5))
        self.assertTrue(isFloat(0))
        self.assertTrue(isFloat('0'))
        self.assertTrue(isFloat(123456))
        self.assertTrue(isFloat('123456'))
        self.assertTrue(isFloat(0.5))
        self.assertTrue(isFloat('0.5'))
        self.assertTrue(isFloat(1235.4567))
        self.assertTrue(isFloat('1235.4567'))
        self.assertFalse(isFloat('5,5'))
        self.assertFalse(isFloat("5 and more"))
        self.assertFalse(isFloat("53.46 and more"))
        self.assertFalse(isFloat("It is just a string"))

    def test_isFloatBetween(self):
        """
        It tests if the function isFloatBetween() works correctly
        """
        for i in range(1000):
            a = random.randint(1, 10000000)
            b = random.randint(1, 10000000)
            if a > b:
                a, b = b, a
            val = random.uniform(a, b - 1)
            self.assertTrue(isFloatBetween(val, a, b))
            float(a)
            float(b)
            float(val)
            self.assertTrue(isFloatBetween(val, a, b))
            val = random.uniform(0.0, a - 1.0)
            self.assertFalse(isFloatBetween(val, a, b))
            val = random.uniform(b + 1.0, 10000001.0)
            self.assertFalse(isFloatBetween(val, a, b))

    def test_isStr(self):
        """
        It tests if the function isStr() works correctly
        """
        for i in range(1000):
            val = random.choice(string.ascii_letters)
            self.assertTrue(isStr(val))
        for i in range(10000):
            val2 = random.randint(1, 10000000)
            self.assertFalse(isStr(val2))
            float(val2)
            self.assertFalse(isStr(val2))

    def test_is_(self):
        """
        It tests if the function is_() works correctly
        """
        for i in range(1000):
            val = random.choice(string.ascii_letters)
            schema = val
            self.assertTrue(is_(val, schema))
            schema = random.choice(string.ascii_letters)
            if (schema != val):
                self.assertFalse(is_(val, schema))
            val = random.randint(1, 100000)
            self.assertFalse(is_(val, schema))
            float(val)
            self.assertFalse(is_(val, schema))

    def test_isShorter(self):
        """
        It tests if the function isShorter() works correctly
        """
        for i in range(1000):
            val = random.choice(string.ascii_letters)
            _int = random.randint(len(val) + 1, 10000)
            self.assertTrue(isShorter(val, _int))
            _int = random.randint(0, len(val) - 1)
            self.assertFalse(isShorter(val, _int))
        for i in range(10000):
            val2 = random.randint(1, 10000000)
            _int = random.randint(1, 10000000)
            self.assertFalse(isShorter(val2, _int))
            float(val2)
            self.assertFalse(isShorter(val2, _int))

    def test_isDict(self):
        """
        It tests if the function isDict() works correctly
        """
        for i in range(1000):
            _dict = generate_rand_dict()
            self.assertTrue(isDict(_dict))
        for i in range(1000):
            value = random.randint(1, 10000)
            self.assertFalse(isDict(value))
            float(value)
            self.assertFalse(isDict(value))
            value = random.choice(string.ascii_letters)
            self.assertFalse(isDict(value))

    def test_isList(self):
        """
        It tests if the function isList() works correctly
        """
        for i in range(1000):
            _list = generate_rand_list()
            self.assertTrue(isList(_list))

    def test_memory_converting(self):
        """
        It tests if the function memory_converting() works correctly
        """
        # error message in case if test case got failed
        message = "First value and second value are not equal!"
        # assertEqual() to check equality of first & second value
        size = 456
        val = str(size) + "B"
        # test for B unit value
        self.assertEqual(bytes_from_str(val), size, message)
        val = str(size) + "K"
        # test for K unit value
        self.assertEqual(bytes_from_str(val), size * 1024, message)
        val = str(size) + "M"
        # test for M unit value
        self.assertEqual(bytes_from_str(val), size * 1024 * 1024, message)
        val = str(size) + "G"
        # test for G unit value
        self.assertEqual(bytes_from_str(val), size * 1024 * 1024 * 1024, message)

    def test_valid_memory_size(self):
        """
        It tests if the function memory_size() works correctly
        """
        unit_list = ['B', 'K', 'M', 'G']
        for i in range(1000):
            size = random.randint(1, 100000)
            max_size = random.randint(size, 100001)
            unit1 = random.choice(unit_list)
            unit2 = random.choice(unit_list)
            if not (compare_memory_unit(unit1, unit2)):
                unit1, unit2 = unit2, unit1  # now unit1 is smaller than unit
            mem_size = str(size) + unit1
            max_mem_size = str(max_size) + unit2
            self.assertTrue(valid_memory_size(mem_size, max_mem_size))

    def test_hasStructure(self):
        """
        It tests if the function hasStructure() works correctly
        """
        # validator at the end of a string
        structure = "set<isInt>"
        self.assertTrue(hasStructure("set123", structure))
        self.assertTrue(hasStructure("set", structure))
        structure = "test_<isIn,'a','wrong','0'>"
        self.assertTrue(hasStructure("test_a", structure))
        self.assertTrue(hasStructure("test_wrong", structure))
        self.assertTrue(hasStructure("test_0", structure))
        # structure at the end and in the middle
        structure = "test<isInt>_set<isInt>"
        self.assertTrue(hasStructure("test123_set123", structure))
        self.assertFalse(hasStructure("test_13_set12", structure))
        self.assertFalse(hasStructure("test12set34", structure))
        self.assertFalse(hasStructure("test123_set", structure))
        self.assertFalse(hasStructure("test_123_set", structure))
        self.assertFalse(hasStructure("test_123", structure))
        # structure at the beginning
        structure = "<isInt>.in"
        self.assertFalse(hasStructure("1. in", structure))
        self.assertFalse(hasStructure("str.in", structure))
        self.assertFalse(hasStructure("2.5.in", structure))

        # two structures with alternative at beginning
        structure = "<isStr>|<isInt>_course"
        self.assertTrue(hasStructure("ASD_course", structure))
        self.assertTrue(hasStructure("MD_course", structure))
        self.assertTrue(hasStructure("123_course", structure))
        # structure at the beginning, middle and at the end
        structure = "<isInt>test<isStr>|<isInt>|<isFloat>"
        self.assertTrue(hasStructure("23test23", structure))
        self.assertTrue(hasStructure("123testSTR", structure))
        self.assertTrue(hasStructure("123test5.67", structure))
        self.assertFalse(hasStructure("test", structure))
        self.assertFalse(hasStructure("34TEST23", structure))

    def test_isAny(self):
        """
        It tests if the function isAny() works correctly
        """
        for i in range(1000):
            val = random.randint(0, 10000000)
            self.assertTrue(isAny(val))
            float(val)
            self.assertTrue(isAny(val))
            str(val)
            self.assertTrue(isAny(val))
            val = random.uniform(0.1, 100000.0)
            self.assertTrue(isAny(val))
            float(val)
            self.assertTrue(isAny(val))
            str(val)
            self.assertTrue(isAny(val))
            a = random.random()
            self.assertTrue(isAny(val))
            float(val)
            self.assertTrue(isAny(val))
            str(val)
            self.assertTrue(isAny(val))
            val = random.choice(string.ascii_letters)
            self.assertTrue(isAny(val))
            _dict = generate_rand_dict()
            self.assertTrue(isAny(_dict))
            _list = generate_rand_list()
            self.assertTrue(isAny(_list))

    def test_isNone(self):
        """
        It tests if the function isNone() works correctly
        """
        for i in range(1000):
            val = random.randint(0, 10000000)
            self.assertFalse(isNone(val))
            float(val)
            self.assertFalse(isNone(val))
            str(val)
            val = random.choice(string.ascii_letters)
            self.assertFalse(isNone(val))
            _dict = generate_rand_dict()
            self.assertFalse(isNone(_dict))
            _list = generate_rand_list()
            self.assertFalse(isNone(_list))
            self.assertTrue(isNone(None))

    def test_isIn(self):
        """
        It tests if the function isIn() works correctly
        """
        rand_int = generate_rand_int()
        rand_float = random.uniform(0.1, 0.9)
        rand_str = random.choice(string.ascii_letters)
        rand_dict = generate_rand_dict()
        rand_list = generate_rand_list()
        self.assertTrue(isIn(rand_int, rand_int, rand_float, rand_str, rand_dict, rand_list))
        self.assertTrue(isIn(rand_float, rand_int, rand_float, rand_str, rand_dict, rand_list))
        self.assertTrue(isIn(rand_str, rand_int, rand_float, rand_str, rand_dict, rand_list))
        self.assertTrue(isIn(rand_dict, rand_int, rand_float, rand_str, rand_dict, rand_list))
        self.assertTrue(isIn(rand_list, rand_int, rand_float, rand_str, rand_dict, rand_list))
        self.assertFalse(isIn(rand_int, rand_float, rand_str, rand_dict))
        self.assertFalse(isIn(rand_list, rand_float, rand_str, rand_dict))
        self.assertFalse(isIn(rand_dict, rand_float, rand_str, rand_list))

    # def test_isPath(self):
    #     """
    #     It tests if the function isPath() works correctly.
    #     """
    #     abs_path = Path("BaCa2/package/packages/tests_to_testing/config.yml").resolve()
    #     self.assertTrue(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/tests_to_testing/1.out").resolve()
    #     self.assertTrue(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/1/config.yml").resolve()
    #     self.assertTrue(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/1/prog/solution.cpp").resolve()
    #     self.assertTrue(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/tests_to_testing/10.out").resolve()
    #     self.assertFalse(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/1/config234.yml").resolve()
    #     self.assertFalse(isPath(abs_path))
    #     abs_path = Path("BaCa2/package/packages/1/prog/sopution.cpp").resolve()
    #     self.assertFalse(isPath(abs_path))


    def size_test(self, size_min, size_max):
        pass

    @parameterized.expand([
        (1, 100),
        (100, 1000),
        (1000, 10000),
        (1, 100000)
    ])
    def test_isSize(self, size_min, size_max):
        """
        It tests if the function isSize() works correctly
        """
        unit_list = ['B', 'K', 'M', 'G']
        for i in range(3000):
            size = random.randint(size_min, size_max)
            max_size = random.randint(size, size_max+1)
            unit1 = random.choice(unit_list)
            unit2 = random.choice(unit_list)
            if not (compare_memory_unit(unit1, unit2)):
                unit1, unit2 = unit2, unit1  # now unit1 is smaller than unit
            mem_size = str(size) + unit1
            max_mem_size = str(max_size) + unit2
            self.assertTrue(isSize(mem_size, max_mem_size),
                            f"mem_size: {mem_size}, max_mem_size: {max_mem_size}")



# It tests the TestF class
class TestFTests(TestCase):
    def setUp(self):
        """
        It creates a test object with the following parameters:
        
        * `Path(__file__).resolve().parent / 'packages' / 'tests_to_testing'` - the path to the directory containing the
        test files.
        * `{}` - the input data for the test.
        * `{'name': '1', 'memory_limit': '10M', 'time_limit': 5}` - the test parameters
        """
        self.test = TF(base_dir() / 'tests_to_testing', {}, {
            'name': '1',
            'memory_limit': '10M',
            'time_limit': 5
        })

    def test_check_valid(self):
        """
        It checks if the test is valid.
        """
        self.assertTrue(self.test.check_test())

    def test_get_settings(self):
        """
        This function tests the get_settings function in the test_settings.py file
        """
        self.assertEqual(self.test['name'], '1')
        self.assertEqual(self.test['memory_limit'], '10M')
        self.assertEqual(self.test['time_limit'], 5)

    def test_set_settings(self):
        """
        It tests that the settings can be set
        """
        self.test['name'] = '2'
        self.assertEqual(self.test['name'], '2')
        self.test['name'] = '1'


# `TestTSet` is a class that tests the class `TSet`
class TSetTests(TestCase):
    def setUp(self):
        """
        The function `setUp` is a method of the class `TestTSet` that creates three instances of the class `TSet` and
        assigns them to the variables `self.set0`, `self.set1`, and `self.set2`
        """
        self.path = base_dir() / '1' / '1' / 'tests'
        self.set0 = TSet(self.path / 'set0')
        self.set1 = TSet(self.path / 'set1')
        self.set2 = TSet(self.path / 'set2')

    def test_init(self):
        """
        `test_init` checks that the `_path` attribute of the `Set` object is equal to the path of the set
        """
        self.assertEqual(self.set0._path, self.path / 'set0')
        self.assertEqual(self.set1._path, self.path / 'set1')
        self.assertEqual(self.set2._path, self.path / 'set2')

    def test_check_valid(self):
        """
        This function checks if the set is valid
        """
        self.assertTrue(self.set0.check_set())
        self.assertEqual(len(self.set0._tests), 2)
        self.assertTrue(self.set1.check_set())
        self.assertTrue(self.set2.check_set())

    def test_func_tests1(self):
        self.assertEqual(self.set0.tests('2'), self.set0._tests[0])
        test = [i for i in self.set1._tests if i['name'] == '2']
        self.assertEqual(self.set1.tests('2'), test[0])
        self.assertEqual(self.set2.tests('3', True), self.set2._tests[3])
        self.set2.delete_test('3')

    def test_func_tests2(self):
        """
        It tests the function tests() in the class TestSet.
        """
        self.assertRaises(NoTestFound, self.set0.tests, '1')
        self.assertRaises(NoTestFound, self.set1.tests, '3')
        self.assertRaises(NoTestFound, self.set2.tests, '2')

    def test_func_delete1(self):
        """
        This function tests the delete_test function in the TestSet class
        """
        self.assertEqual(self.set0.tests('4', True), self.set0._tests[2])
        self.set0.delete_test('4')
        names = [i['name'] for i in self.set0._tests]
        self.assertNotIn('4', names)

    def test_func_delete2(self):
        """
        It checks if the test is in the set.
        """
        self.assertRaises(NoTestFound, self.set0.tests, '1')
        self.assertRaises(NoTestFound, self.set1.tests, '3')
        self.assertRaises(NoTestFound, self.set2.tests, '2')

    def test_func_move1(self):
        """
        It moves a test from one test set to another.
        """
        self.set2.move_test('5', self.set1)
        names = [i['name'] for i in self.set1._tests]
        self.assertIn('5', names)
        self.set1.move_test('5', self.set2)

    def test_func_move2(self):
        """
        It moves a test from one set to another.
        """
        self.set2.move_test('6', self.set1)
        with open(self.set1._path / 'config.yml', mode="rt", encoding="utf-8") as file:
            settings = safe_load(file)
        value = False
        for i in settings['tests'].values():
            if i['name'] == '6':
                value = True
        self.assertTrue(value)
        self.set1.move_test('6', self.set2)

    def test_func_move2(self):
        """
        It tests if the function tests() raises an error when the test number is not found.
        """
        self.assertRaises(NoTestFound, self.set0.tests, '1')
        self.assertRaises(NoTestFound, self.set1.tests, '3')
        self.assertRaises(NoTestFound, self.set2.tests, '2')


# It tests the package class
class PackageTests(TestCase):
    def setUp(self):
        """
        The function takes a path to a package and returns a package object
        """
        self.path = base_dir() / '1'
        self.package = Package(self.path, commit='1')
        self.path = self.path / '1'

    def test_init(self):
        """
        The function tests that the package's path is the same as the path that was passed to the function, and that the
        package's title is the same as the title in the config.yml file
        """
        self.assertEqual(self.package.commit_path, self.path)
        with open(self.path / 'config.yml', mode="rt", encoding="utf-8") as file:
            settings = safe_load(file)
        self.assertEqual(self.package['title'], settings['title'])

    def test_func_sets1(self):
        """
        It tests if the function sets() returns the correct set.
        """
        self.assertIn(self.package.sets('set0'), self.package._sets)

    def test_func_sets2(self):
        """
        It tests that the function sets() raises an exception when it is passed a set that does not
        exist.
        """
        self.assertRaises(NoSetFound, self.package.sets, 'set3')

    def test_func_sets3(self):
        """
        This function tests the sets function in the package class
        """
        self.package.sets('set4', True)
        sets = [i['name'] for i in self.package._sets]
        self.assertIn('set4', sets)
        self.assertTrue(self.package.sets('set4')._path.exists())
        self.package.delete_set('set4')

    def test_func_delete(self):
        """
        This function tests the delete function of the package class
        """
        self.assertRaises(NoSetFound, self.package.sets, 'set4')

    def test_check_valid(self):
        """
        It checks if the package is valid.
        """
        self.assertTrue(self.package.check_package())

    def test_make_commit(self):
        """
        It tests if the function make_commit() works.
        """
        new_comm = self.package.make_commit('2')
        self.assertIsInstance(new_comm, Package)
        self.assertEqual(new_comm._commit, '2')
        shutil.rmtree(new_comm.commit_path)

    def test_make_commit_and_delete(self):
        """
        It tests if deleting commit works.
        """
        new_comm = self.package.make_commit('3')
        self.assertIsInstance(new_comm, Package)
        self.assertEqual(new_comm._commit, '3')
        path_to_comm = new_comm.commit_path
        new_comm.delete()
        self.assertFalse(path_to_comm.exists())

    def test_prepare_build(self):
        """
        It tests if the function prepare_build() works.
        """
        self.package.prepare_build('test')
        self.assertTrue((self.package.commit_path / '.build' / 'test').is_dir())
        self.package.delete_build('test')
        self.assertFalse((self.package.commit_path / '.build' / 'test').is_dir())

    def test_prepare_build_multiple(self):
        """
        It tests if the function prepare_build() works.
        """
        self.package.prepare_build('test')
        self.package.prepare_build('test2')
        self.assertTrue((self.package.commit_path / '.build' / 'test').is_dir())
        self.package.delete_build()
        self.assertFalse((self.package.commit_path / '.build').is_dir())

    def test_doc_extension_check(self):
        """
        It tests if the doc_extension function works.
        """
        self.assertEqual(self.package.doc_extension('pdf'), 'md')
        self.assertEqual(self.package.doc_extension(), 'md')
        doc_file = self.package.doc_path('md')
        self.assertTrue(doc_file.is_file())

    def test_doc_path(self):
        """
        It tests if the doc_path function works.
        """
        with self.assertRaises(InvalidFileExtension):
            self.package.doc_path('x')
        with self.assertRaises(FileNotFoundError):
            self.package.doc_path('pdf')

    def test_docs_to_display_all(self):
        """
        It tests if the get_docs_to_display function works.
        """
        docs = self.package.get_docs_to_display(best_and_pdf=False)
        self.assertEqual(len(docs), 2)
        for doc in docs:
            self.assertTrue(doc.is_file())
            self.assertTrue(doc.suffix in ('.md', '.txt'))

    def test_docs_to_display_best_and_pdf(self):
        """
        It tests if the get_docs_to_display function works.
        """
        docs = self.package.get_docs_to_display(best_and_pdf=True)
        self.assertEqual(len(docs), 1)
        self.assertTrue(docs[0].is_file())
        self.assertTrue(docs[0].suffix == '.md')

class PackageZip(TestCase):
    def setUp(self):
        self.test_base = Path(__file__).parent / 'test_packages'
        self.zip_path = self.test_base / 'zip_src'
        self.pkg_path = self.test_base / 'zip_pkg'

    def tearDown(self):
        if self.pkg_path.exists():
            shutil.rmtree(self.pkg_path)

    def test_01_create_simple_package(self):
        """
        Tests creating simple package from zip file, checks primary values
        """
        pkg = Package.create_from_zip(self.pkg_path, '1', self.zip_path / 'test_pkg.zip')
        self.assertEqual(pkg['title'], 'zip test pkg')
        self.assertEqual(pkg['points'], 123)

    def test_02_create_simple_package_depth_test(self):
        """
        Tests creating simple package from zip file, checks in-depth values
        """
        pkg = Package.create_from_zip(self.pkg_path, '1', self.zip_path / 'test_pkg.zip')
        self.assertEqual(pkg['title'], 'zip test pkg')

        set1 = pkg.sets('set1')
        self.assertEqual(set1['name'], 'set1')
        self.assertEqual(set1['points'], 10)
        test1 = set1.tests('1')
        with open(test1['input'], 'r') as f:
            self.assertEqual(f.read(), 'set1 in')
        with open(test1['output'], 'r') as f:
            self.assertEqual(f.read(), 'set1 out')
