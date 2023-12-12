import setuptools
import urllib.request
import json

from pkg_resources import parse_version

MANUAL_VERSION = None


def list_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"

    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read().decode('utf-8'))

    versions = data['releases']

    return sorted(versions, key=parse_version, reverse=True)


def version(new_version: bool = False) -> str:
    """
    Returns version of the new package, by elevating the version of the old package. Or returns the
    manual version.
    """
    versions = list_versions('baca2-package-manager')
    v = versions[0]
    if len(versions) == 0:
        v = '0.0.1'

    if not new_version:
        return v

    if MANUAL_VERSION is not None:
        mv = MANUAL_VERSION
        if mv not in versions:
            v = mv

    new_v = v.split('.')
    new_v[-1] = str(int(new_v[-1]) + 1)
    new_v = '.'.join(new_v)
    return new_v


setuptools.setup(
    name='baca2-package-manager',
    version=version(new_version=True),
    author='Baca2 Team',
    author_email='bartosz.deptula@student.uj.edu.pl',
    description='A package manager for Baca2 project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BaCa2-project/BaCa2-package-manager',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    python_requires='>=3.11',
    install_requires=[
        'pyyaml',
    ]
)
