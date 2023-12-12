import setuptools
from version_elevator import version

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
