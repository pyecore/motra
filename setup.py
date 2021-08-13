#!/usr/bin/env python

import sys
from setuptools import setup
import motra

packages = ['motra',
            'motra.trace']

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')

setup(
    name='motra',
    version=motra.__version__,
    description=('A Python(ic) implementation of the UML2 metamodel'),
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    keywords='model metamodel MDE M2M M2T traceability transformation',
    url='https://github.com/pyecore/pyuml2',
    author='Vincent Aranega',
    author_email='vincent.aranega@gmail.com',

    packages=packages,
    package_data={'': ['README.rst', 'LICENSE', 'CHANGELOG.rst']},
    include_package_data=True,
    install_requires=['pyecore'],
    tests_require=['pytest'],
    license='BSD 3-Clause',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: BSD License',
    ]
)
