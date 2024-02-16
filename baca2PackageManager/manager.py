from __future__ import annotations

import shutil
from copy import deepcopy
from enum import Enum
from pathlib import Path
from os import remove, replace, walk, mkdir, rename, listdir
from shutil import rmtree, copytree
from typing import List, Self

from yaml import safe_load, dump
from re import match

from .judge_manager import JudgeManager
from .validators import isAny, isNone, isInt, isIntBetween, isFloat, isFloatBetween, isStr, is_, \
    isIn, isShorter, \
    isDict, isPath, isSize, isList, valid_memory_size, isBool
from .tools import bytes_from_str
from .consts import SUPPORTED_EXTENSIONS, BASE_DIR
from .manager_exceptions import NoTestFound, NoSetFound, TestExistError, FileAlreadyExist, \
    InvalidFileExtension, PackageCreationFailed

__all__ = ['Package', 'TSet', 'TestF']

from .zipper import Zip


def merge_settings(default: dict, to_add: dict) -> dict:
    """
    It takes two dictionaries, and returns a new dictionary that has the keys of the first dictionary, and the values of the
    second dictionary if they exist, otherwise the values of the first dictionary. It overwrites default dict with valuses from to_add

    :param default: The default settings
    :type default: dict
    :param to_add: The settings you want to add to the default settings
    :type to_add: dict

    :return: A dictionary with the keys of the default dictionary and the values of the to_add dictionary.
    """
    new = {}
    for i in default.keys():
        if to_add is not None:
            if i in to_add.keys() and to_add[i] is not None:
                new[i] = to_add[i]
            else:
                new[i] = default[i]
        else:
            new[i] = default[i]
    return new


class PackageManager:
    """
    It's a class that manages a package's settings
    """

    def __init__(self, path: Path, settings_init: Path or dict, default_settings: dict):
        """
        If the settings_init is a dict, assign it to settings. If not, load the settings_init yaml file and assign it to
        settings. Then merge the settings with the default settings

        :param path: Path to the settings file
        :type path: Path
        :param settings_init: This is the path to the settings file
        :type settings_init: Path or dict
        :param default_settings: a dict with default settings
        :type default_settings: dict
        """
        self._path = path
        # if type of settings_init is a dict assign settings_init to processed settings
        settings = {}
        if type(settings_init) == dict:
            if bool(settings_init):
                settings = settings_init
        # if not, make dict from settings_init yaml
        else:
            # unpacking settings file to dict
            with open(settings_init, mode="rt", encoding="utf-8") as file:
                settings = safe_load(file)
        # merge external settings with default
        self._settings = merge_settings(default_settings, settings)

    def __getitem__(self, arg: str):
        """
        If the key is in the dictionary, return the value. If not, raise a KeyError

        :param arg: The name of the key to get the value of
        :type arg: str

        :return: The value of the key in the dictionary.
        """
        try:
            return self._settings[arg]
        except KeyError:
            raise KeyError(f'No key named {arg} has found in self_settings')

    def get(self, arg: str, default=None):
        try:
            return self._settings[arg]
        except KeyError:
            return default

    def __setitem__(self, arg: str, val):
        """
        `__setitem__` is a special method that allows us to use the `[]` operator to set a value in a dictionary

        :param arg: str
        :type arg: str
        :param val: the value to be set
        """
        self._settings[arg] = val
        # effect changes to yaml settings
        self.save_to_config(self._settings)

    def check_validation(self, validators) -> bool:
        """
        It checks if the value of the setting is valid by checking if it matches any of the validators for that setting

        :param validators: A dictionary of validators. The keys are the names of the settings, and the values are lists of
        validators. Each validator is a tuple of the form (function, *args, **kwargs). The function is called with the
        setting value as the first argument, followed by the *

        :return: The check variable is being returned.
        """
        for i, j in self._settings.items():
            check = False
            for k in validators[i]:
                check |= k[0](j, *k[1:])
        return check

    def save_to_config(self, settings):
        """
        It opens a file called config.yml in the directory specified by the path attribute of the object, and writes the
        settings dictionary to it.

        :param settings: The settings to save
        """
        with open(self._path / 'config.yml', mode="wt", encoding="utf-8") as file:
            dump(settings, file)

    def read_from_config(self):
        """
        It reads the config.yml file from the path and returns the contents

        :return: The dict from config.yml file is being returned.
        """
        with open(self._path / 'config.yml', mode="rt", encoding="utf-8") as file:
            return safe_load(file)

    def add_empty_file(self, filename):
        """
        It creates an empty file if it doesn't already exist

        :param filename: The name of the file to be created
        """
        if not isPath(self._path / filename):
            with open(self._path / filename, 'w') as f:
                pass

    def __iter__(self):
        """
        It returns an iterator for the settings dictionary

        :return: The iterator for the settings dictionary
        """
        return iter(self._settings.items())


class Package(PackageManager):
    """
    It's a class that represents a package.
    """

    #: Largest file acceptable to upload
    MAX_SUBMIT_MEMORY = '10G'
    #: Largest acceptable submit time
    MAX_SUBMIT_TIME = 600
    MAX_CPUS = 16
    MAX_SOURCE_SIZE = '512M'
    SETTINGS_VALIDATION = {
        'title': [[isStr]],
        'points': [[isInt], [isFloat]],
        'memory_limit': [[isSize, MAX_SUBMIT_MEMORY]],
        'source_memory': [[isSize, MAX_SOURCE_SIZE]],
        'time_limit': [[isIntBetween, 0, MAX_SUBMIT_TIME], [isFloatBetween, 0, MAX_SUBMIT_TIME]],
        'allowedExtensions': [[isIn, *SUPPORTED_EXTENSIONS],
                              [isList, [isIn, *SUPPORTED_EXTENSIONS]]],
        'hinter': [[isNone], [isPath]],
        'checker': [[isNone], [isPath]],
        'test_generator': [[isNone], [isPath]],
        'network': [[isNone], [isBool]],
        'cpus': [[isNone], [isIntBetween, 1, MAX_CPUS]]
    }
    """
    Validation for ``Package`` settings.
    
    Available options are:
    
        * ``title``: package name
        * ``points``: maximum amount of points to earn
        * ``memory_limit``: is a memory limit
        * ``time_limit``: is a time limit
        * ``allowedExtensions``: extensions witch are accepted
        * ``hinter``: is a path or None value to actual hinter
        * ``checker``: is a path or None value to actual checker
        * ``test_generator``: is a path or None value to actual generator
        * ``network``: is a bool value to allow network access
        * ``cpus``: is a number of cpus to use
    """

    #: Default values for Package settings
    DEFAULT_SETTINGS = {
        'title': '<no-name>',
        'points': 0,
        'memory_limit': '512M',
        'time_limit': 10,
        'allowedExtensions': 'cpp',
        'hinter': None,
        'checker': None,
        'test_generator': None,
        'network': False,
        'cpus': 1
    }

    # TODO: Add auto-discovery of judge manager files

    class DocExtension(Enum):
        """
        Defines the allowed extensions for task description files
        """
        HTML = 'html'
        MD = 'md'
        PDF = 'pdf'
        TXT = 'txt'

        @classmethod
        def allowed_extensions(cls) -> List[str]:
            """
            :return: List of allowed extensions
            :rtype: List[str]
            """
            return [e.value for e in cls]

        @classmethod
        def from_str(cls, ext: str) -> Self:
            """
            Creates an instance of DocExtension from string, checking if the extension is valid

            :param ext: The extension
            :type ext: str
            :return: Instance of DocExtension
            :rtype: DocExtension

            :raise InvalidFileExtension: If the extension is not valid
            """
            if ext.lower() not in cls.allowed_extensions():
                raise InvalidFileExtension(f'"{ext}" is not valid extension for task description')
            return cls[ext.upper()]

    def __init__(self, path: Path, commit: str, validate_pkg: bool = False) -> None:
        """
        It takes a path to a folder, and then it creates a list of all the subfolders in that folder, and then it creates a
        TSet object for each of those subfolders

        :param path: Path - the path to the package
        :type path: Path
        """
        self._path = path
        self._commit = commit

        config_path = self.commit_path / 'config.yml'
        if not config_path.is_file():
            config_path = self.commit_path / 'config.yaml'
        sets_path = self.commit_path / 'tests'
        super().__init__(path, config_path, Package.DEFAULT_SETTINGS)
        self._sets = []
        self.judge_manager = None
        for i in [x[0].replace(str(sets_path) + '\\', '') for x in walk(sets_path)][1:]:
            self._sets.append(TSet(sets_path / i))
        if validate_pkg:
            self.check_package()

    @classmethod
    def create_from_zip(cls,
                        path: Path,
                        commit: str,
                        zip_path: Path,
                        overwrite: bool = False) -> Self:
        """
        It takes a path to a zip file, and then it extracts it to a folder, and then it creates a Package object from that
        folder

        :param path: Path - the path to the zip file
        :type path: Path
        :param commit: The commit of the package
        :type commit: str
        :param zip_path: The path to the zip file
        :type zip_path: Path
        :param overwrite: If True, it will overwrite the package if it already exists,
            defaults to False
        :type overwrite: bool, optional

        :return: The Package object
        :rtype: Package
        """
        pkg_path = path / commit
        if pkg_path.is_dir():
            if overwrite:
                rmtree(pkg_path)
            else:
                raise FileAlreadyExist(f'Files already exists in {pkg_path}')
        pkg_path.mkdir(parents=True)
        try:
            with Zip(zip_path, 'r') as zip_f:
                zip_f.extractall(pkg_path, leave_top=False)

            pkg = cls(path, commit, validate_pkg=True)
        except Exception as e:
            rmtree(pkg_path)
            if not any(path.iterdir()):
                rmtree(path)

            raise PackageCreationFailed(e, root_path=pkg_path)
        return pkg

    @property
    def name(self) -> str:
        """
        :return: It returns the name of the package
        """
        return self._settings['title']

    def set_judge_manager(self, judge_manager: JudgeManager):
        self.judge_manager = judge_manager

    @property
    def judge_manager_path(self) -> Path:
        jm_path = self.commit_path / 'sequence.judge'
        if not jm_path.is_file():
            raise FileNotFoundError(f'Judge manager file not found in {self.commit_path}')
        return jm_path

    def prepare_build(self, build_name: str):
        """
        It prepares the build

        :param build_name: The name of the build
        :type build_name: str
        """
        if not (self.commit_path / '.build').is_dir():
            mkdir(self.commit_path / '.build')

        build_dir = self.commit_path / '.build' / build_name

        if build_dir.is_dir():
            rmtree(build_dir)
        mkdir(build_dir)

        return build_dir

    def build_path(self, build_name: str) -> Path:
        """
        It returns the path to the build

        :param build_name: The name of the build
        :type build_name: str

        :return: The path to the build
        :rtype: Path
        """
        return self.commit_path / '.build' / build_name

    def check_build(self, build_name: str) -> bool:
        """
        It checks if the build exists

        :param build_name: The name of the build
        :type build_name: str

        :return: True if the build exists, False otherwise
        :rtype: bool
        """
        build_dir = self.build_path(build_name)

        if not build_dir.is_dir():
            return False

        return any(list(walk(build_dir))[0][1:])

    def delete_build(self, build_name: str = None):
        """
        Deletes the build. If build_name is None, it deletes all builds.

        :param build_name: The name of the build, if None, it clears all builds
        :type build_name: str
        """
        if build_name is None:
            rmtree(self.commit_path / '.build')
        else:
            rmtree(self.commit_path / '.build' / build_name)

    @property
    def commit_path(self) -> Path:
        """
        It returns the path to the commit
        TODO: After implementing internal git system, this should be changed

        :return: The path to the commit
        :rtype: Path
        """
        return self._path / self._commit

    def rm_tree(self, set_name):
        """
        It removes a directory tree

        :param set_name: The name of the test set
        """
        if isPath(self.commit_path / 'tests' / set_name):
            rmtree(self.commit_path / 'tests' / set_name)

    def make_commit(self, new_commit: str) -> 'Package':
        """
        Function copies the package instance and creates new one/

        :param new_path: The path of the package
        :param new_commit: New unique commit

        :return: new Package
        """
        new_commit_path = self._path / new_commit
        copytree(self.commit_path, new_commit_path)
        return Package(self._path, new_commit)

    def delete(self) -> None:
        """
        Function deletes the package (itself) from directory

        :return: None
        """
        rmtree(self.commit_path)
        del self

    def _add_new_set(self, set_name) -> 'TSet':
        """
        This function adds a new test set to the test suite

        :param set_name: The name of the new test set

        :return: A new TSet object.
        """
        settings = {'name': set_name} | self._settings
        set_path = self.commit_path / 'tests' / set_name
        if not isPath(set_path):
            mkdir(set_path)
            with open(set_path / 'config.yml', 'w') as file:
                dump({'name': set_name}, file)
        new_set = TSet(set_path)
        self._sets.append(new_set)
        return new_set

    def sets(self, set_name: str = None, add_new: bool = False) -> TSet or List[TSet]:
        """
        It returns the set with the name `set_name` if it exists, otherwise it raises an error
        If set_name is None, it returns list of all sets.

        :param set_name: The name of the set you want to get (if none it returns all sets)
        :type set_name: str
        :param add_new: If True, it will create a new set directory if it doesn't exist, defaults to False
        :type add_new: bool (optional)

        :return: The set with the name set_name, or a list of all sets
        :rtype: TSet or List[TSet]
        """
        if set_name is None:
            return self._sets

        for i in self._sets:
            if i['name'] == set_name:
                return i
        if add_new:
            self._add_new_set(set_name)
        else:
            raise NoSetFound(f'Any set directory named {set_name} has found')

    def delete_set(self, set_name: str):
        """
        It deletes a set from the sets list and removes the directory of the set

        :param set_name: The name of the set you want to delete
        :type set_name: str
        :return: the list of sets.
        """
        for i in self._sets:
            if i['name'] == set_name:
                self._sets.remove(i)
                self.rm_tree(set_name)
                return
        raise NoSetFound(f'Any set directory named {set_name} has found to delete')

    def check_package(self, subtree: bool = True) -> bool | int:
        """
        It checks the package.

        :param subtree: bool = True, defaults to True
        :type subtree: bool (optional)
        :return: The result of the check_validation() method and the result of the check_set() method.
        """
        result = True
        # check doc file
        try:
            self.doc_extension()
        except FileNotFoundError:
            return False

        # check sets
        if subtree:
            for i in self._sets:
                result &= i.check_set()

        # check package
        return self.check_validation(Package.SETTINGS_VALIDATION) & result

    def doc_path(self, extension: str | DocExtension) -> Path:
        """
        It returns the path to the task description file with the given extension.

        Valid extensions are:

        * PDF
        * MD
        * HTML
        * TXT

        :param extension: The extension of the file
        :type extension: str
        :return: The path to the task description file
        :rtype: Path

        :raise FileNotFoundError: If the file with the given extension doesn't exist
        """
        if isinstance(extension, str):
            extension = self.DocExtension.from_str(extension)
        doc_path = self.commit_path / 'doc'
        path = None
        for f in doc_path.iterdir():
            if f.suffix == f'.{extension.value}':
                path = f
                break
        if not (path and path.is_file()):
            raise FileNotFoundError(f'"{extension.name}" is not valid extension for '
                                    f'{self.get("title")} task description')
        return path

    def doc_has_extension(self, extension: str | DocExtension) -> bool:
        """
        It checks if the task description file has the given extension.

        Valid extensions are:

        * PDF
        * MD
        * HTML
        * TXT

        :param extension: The extension of the file
        :type extension: str
        :return: True if the file with the given extension exists, False otherwise
        :rtype: bool
        """
        try:
            self.doc_path(extension)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(e)
            return False

    def doc_extension(self, prefere_extension: str = None) -> str:
        """
        It returns the extension of the task description file. If prefere_extension is not None,
        and the file with the given extension exists, it returns the given extension. Otherwise
        it returns the first found extension.

        :param prefere_extension: The preferred extension
        :type prefere_extension: str

        :return: The extension of the task description file
        :rtype: str

        :raise FileNotFoundError: If no file with valid extension exists.
        """
        if prefere_extension is not None:
            prefere_extension = self.DocExtension.from_str(prefere_extension)
            try:
                self.doc_path(prefere_extension)
                return prefere_extension.value
            except FileNotFoundError:
                pass

        for ext in self.DocExtension:
            try:
                self.doc_path(ext)
                return ext.value
            except FileNotFoundError:
                pass
        raise FileNotFoundError(f'No task description file found for {self.get("title")}')

    def get_docs_to_display(self, best_and_pdf: bool = True) -> List[Path]:
        """
        It returns the list of paths to the task description files.

        :return: The list of paths to the task description files
        :rtype: List[Path]
        """
        docs = []
        if not best_and_pdf:
            for ext in self.DocExtension:
                try:
                    docs.append(self.doc_path(ext))
                except FileNotFoundError:
                    pass
            return docs

        try:
            docs.append(self.doc_path('pdf'))
        except FileNotFoundError:
            pass
        for ext in self.DocExtension:
            if ext.value == 'pdf':
                continue
            try:
                docs.append(self.doc_path(ext))
                return docs
            except FileNotFoundError:
                pass


class TSet(PackageManager):
    """
    It's a class that represents a set of tests and modifies it
    """
    SETTINGS_VALIDATION = {
        'name': [[isStr]],
        'weight': [[isInt], [isFloat]],
        'points': [[isInt], [isFloat]],
        'memory_limit': [[isNone], [isSize, Package.MAX_SUBMIT_MEMORY]],
        'time_limit': [[isNone], [isIntBetween, 0, Package.MAX_SUBMIT_TIME],
                       [isFloatBetween, 0, Package.MAX_SUBMIT_TIME]],
        'checker': [[isNone], [isPath]],
        'test_generator': [[isNone], [isPath]],
        'tests': [[isNone], [isAny]],
        'makefile': [[isNone], [isPath]]
    }

    """
        Validation for ``TSet`` settings.

        Available options are:
            * ``name``: set name
            * ``weight``: impact of set score on final score
            * ``points``: maximum amount of points to earn in set
            * ``memory_limit``: is a memory limit for set
            * ``time_limit``: is a time limit for set
            * ``checker``: is a path or None value to actual checker
            * ``test_generator``: is a path or None value to actual generator
            * ``tests``: tests to run in set
            * ``makefile``: name of a makefile
        """
    #: Default values for set settings
    DEFAULT_SETTINGS = {
        'name': '_unnamed',
        'weight': 10,
        'points': 0,
        'memory_limit': '512M',
        'time_limit': 10,
        'checker': None,
        'test_generator': None,
        'tests': {},
        'makefile': None
    }

    def __init__(self, path: Path):
        """
        It reads the config file and creates a list of tests

        :param path: Path - path to the test set
        :type path: Path
        """
        config_path = path / 'config.yml'
        if not config_path.is_file():
            config_path = path / 'config.yaml'
        if not config_path.is_file():
            config_path = {}
        super().__init__(path, config_path, TSet.DEFAULT_SETTINGS)
        if self['name'] == '_unnamed':
            self['name'] = path.name
        self._tests = []
        self._test_settings = {
            'name': '0',
            'memory_limit': self._settings['memory_limit'],
            'time_limit': self._settings['time_limit'],
            'points': 0
        }
        if self._settings['tests'] is not None:
            for i in self._settings['tests'].values():
                self._tests.append(TestF(path, i, self._test_settings))
        self._add_test_from_dir()

    def move_test_file(self, to_set, filename):
        """
        It moves a file from one directory to another

        :param to_set: the set you want to move the file to
        :param filename: the name of the file to move
        """
        if isPath(to_set._path):
            if isPath(self._path / filename):
                replace(self._path / filename, to_set._path / filename)

    def _add_test_from_dir(self):
        """
        It takes a directory, finds all the files in it, and then adds all the tests that have both an input and output file
        """
        test_files_ext = listdir(self._path)
        tests = []
        for i in test_files_ext:
            tests.append(match('.*[^.in|out]', i).group(0))
        tests_to_do = []
        for i in tests:
            if tests.count(i) == 2:
                tests_to_do.append(i)
        tests_to_do = set(tests_to_do)
        names = [i["name"] for i in self._tests]
        for i in tests_to_do:
            if i not in names:
                name_dict = {'name': i}
                self._tests.append(TestF(self._path, name_dict, self._test_settings))

    def tests(self, test_name: str = None, add_new: bool = False) -> 'TestF' or List['TestF']:
        """
        It returns a test object with the given name, if it exists, or creates a new one if it doesn't
        If no name is given, it returns a list of all the tests.

        :param test_name: The name of the test, if None, it returns a list of all the tests, defaults to None
        :type test_name: str
        :param add_new: if True, then if the test is not found, it will be created, defaults to False
        :type add_new: bool (optional)

        :return: A TestF object or a list of TestF objects
        :rtype: TestF or List[TestF]
        """
        if test_name is None:
            return self._tests
        for i in self._tests:
            if i['name'] == test_name:
                return i
        if add_new:
            new_test = TestF(self._path, {'name': test_name}, self._test_settings)
            self._tests.append(new_test)
            self.add_empty_file(test_name + '.in')
            self.add_empty_file(test_name + '.out')
            return new_test
        raise NoTestFound(f'Any test named {test_name} has found')

    def remove_file(self, filename):
        """
        It removes a file from the current directory

        :param filename: The name of the file to remove
        """
        if isPath(self._path / filename):
            remove(self._path / filename)

    def _delete_chosen_test(self, test: 'TestF'):
        """
        It removes the test from the list of tests, deletes the files associated with the test,
        and removes the test from the config file

        :param test: the test to be deleted
        :type test: 'TestF'
        """
        self._tests.remove(test)
        self.remove_file(test['name'] + '.in')
        self.remove_file(test['name'] + '.out')

        # removes settings for this test (from _settings and from config file)
        new_settings = deepcopy(self._settings)
        for k, v in self._settings['tests'].items():
            if v['name'] == test['name']:
                new_settings['tests'].pop(k)
        self._settings = new_settings
        self.save_to_config(self._settings)

    def delete_test(self, test_name: str):
        """
        It deletes a test from the list of tests, and deletes associated files.

        :param test_name: The name of the test to delete
        :type test_name: str
        :raise NoTestsFound: If there is no test with name equal to the test_name argument.
        """
        for test in self._tests:
            if test['name'] == test_name:
                self._delete_chosen_test(test)
                return

        raise NoTestFound(f'No test named {test_name} has found to delete')

    def _move_chosen_test(self, test: 'TestF', to_set: 'TSet'):
        """
         Move a test from one test set to another

        :param test: 'TestF' - the test to be moved
        :type test: 'TestF'
        :param to_set: the set to which the test will be moved
        :type to_set: 'TSet'
        """
        name_list_ta = [j['name'] for j in to_set._tests]
        if test['name'] not in name_list_ta:
            to_set._tests.append(test)
            self._tests.remove(test)
        else:
            raise TestExistError(f'Test named {test["name"]} exist in to_set files')

        self.move_test_file(to_set, test['name'] + '.in')
        self.move_test_file(to_set, test['name'] + '.out')

    def _move_config(self, to_set: 'TSet', test_name: str):
        """
        It takes a test name and a set object, and moves the test from the current set to the set object

        :param to_set: The set to move the test to
        :type to_set: 'TSet'
        :param test_name: The name of the test you want to move
        :type test_name: str
        """
        new_settings = deepcopy(self._settings)
        for i, j in self._settings['tests'].items():
            if j['name'] == test_name:
                to_set._settings['tests'][i] = j
                new_settings['tests'].pop(i)

        self._settings = new_settings
        self.remove_file('config.yml')
        self.save_to_config(self._settings)
        to_set.remove_file('config.yml')
        to_set.save_to_config(to_set._settings)

    # moves test to to_set (and all settings pinned to this test in self._settings)
    def move_test(self, test_name: str, to_set: 'TSet'):
        """
        It moves a test from one set to another

        :param test_name: The name of the test to move
        :type test_name: str
        :param to_set: The set to which the test will be moved
        :type to_set: 'TSet'
        """
        search = False
        for i in self._tests:
            if i['name'] == test_name:
                self._move_chosen_test(i, to_set)
                self._move_config(to_set, test_name)
                search |= True
                return
            search |= False

        if not search:
            raise NoTestFound(f'Any test named {test_name} has found to move to to_set')

    # check set validation
    def check_set(self, subtree=True) -> bool | int:
        """
        It checks the set.

        :param subtree: If True, check the subtree of tests, defaults to True (optional)

        :return: The result of the check_validation() method and the result of the check_set() method.
        """
        result = True
        if subtree:
            for i in self._tests:
                result &= i.check_test()

        return self.check_validation(TSet.SETTINGS_VALIDATION) & result


class TestF(PackageManager):
    """
    It's a class that represents test in a set.
    """
    SETTINGS_VALIDATION = {
        'name': [[isStr]],
        'memory_limit': [[isNone], [isSize, Package.MAX_SUBMIT_MEMORY]],
        'time_limit': [[isNone], [isIntBetween, 0, Package.MAX_SUBMIT_TIME],
                       [isFloatBetween, 0, Package.MAX_SUBMIT_TIME]],
        'points': [[isInt], [isFloat]],
        'input': [[isNone], [isPath]],
        'output': [[isNone], [isPath]],
    }
    """
       Validation for ``TestF`` settings.

       Available options are:
        * ``name``: test name
        * ``points``: maximum amount of points to earn in test
        * ``memory_limit``: is a memory limit for test
        * ``time_limit``: is a time limit for test
        * ``input``: is a path or None value to actual input
        * ``output``: is a path or None value to actual output
       """

    def __init__(self, path: Path, additional_settings: dict or Path, default_settings: dict):
        """
        This function initializes the class by calling the superclass's __init__ function, which is the __init__ function of
        the Config class

        :param path: The path to the file that contains the settings
        :type path: Path
        :param additional_settings: This is a dictionary of settings that you want to override the default settings with
        :type additional_settings: dict or Path
        :param default_settings: This is a dictionary of default settings that will be used if the settings file doesn't
        contain a value for a setting
        :type default_settings: dict
        """
        super().__init__(path, additional_settings, default_settings)
        input_file = self._path / (self._settings['name'] + '.in')
        if input_file.is_file():
            self._settings['input'] = input_file
        output_file = self._path / (self._settings['name'] + '.out')
        if output_file.is_file():
            self._settings['output'] = output_file

    def _rename_files(self, old_name, new_name):
        """
        It renames a file

        :param old_name: The name of the file you want to rename
        :param new_name: The new name of the file
        """
        rename(self._path / old_name, self._path / new_name)

    def __setitem__(self, arg: str, val):
        """
        It renames the files and changes the name in the yaml file

        :param arg: the key of the dictionary
        :type arg: str
        :param val: the new value
        """
        # effect changes to yaml settings
        settings = self.read_from_config()
        if arg == 'name':
            self._rename_files(self._settings['name'] + '.in', val + '.in')
            self._rename_files(self._settings['name'] + '.out', val + '.out')

            for i, j in settings['tests'].items():
                if j['name'] == self._settings['name']:
                    new_key = 'test' + val
                    j[arg] = val
                    settings['tests'][new_key] = j
                    del settings['tests'][i]
                    break

        self.save_to_config(settings)
        self._settings[arg] = val

    def check_test(self) -> bool:
        """
        It checks if the test is valid
        :return: The return value is the result of the check_validation method.
        """
        return self.check_validation(TestF.SETTINGS_VALIDATION)
