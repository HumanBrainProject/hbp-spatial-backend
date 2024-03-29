#!/usr/bin/env python3

import codecs
import os.path
import re
import sys

import setuptools


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def find_source_url(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^SOURCE_URL = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find SOURCE_URL string.")


# Remember keep synchronized with the list of dependencies in
# test-requirements.txt.
tests_require = [
    "pytest",
    "requests ~= 2.5",
]

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setuptools.setup(
    name="hbp-spatial-backend",
    version=find_version("hbp_spatial_backend", "__init__.py"),
    packages=["hbp_spatial_backend"],
    url=find_source_url("hbp_spatial_backend", "__init__.py"),
    author="Yann Leprince",
    author_email="yann.leprince@cea.fr",
    install_requires=[
        "Flask ~= 1.0",
        "Flask-Cors",
        "flask-smorest ~= 0.18.4",
        "marshmallow ~= 3.0",
        # see https://github.com/yaml/pyyaml/issues/601
        # see https://github.com/yaml/pyyaml/issues/723
        # see https://github.com/yaml/pyyaml/issues/724
        "PyYAML ~= 6.0.1",
        # see https://stackoverflow.com/questions/72191560/importerror-cannot-import-name-soft-unicode-from-markupsafe # noqa: E501
        "markupsafe==2.0.1",
    ],
    python_requires="~= 3.5",
    extras_require={
        "dev": tests_require + [
            "check-manifest",
            "flake8",
            "pep8-naming",
            "pre-commit",
            "pytest-cov",
            "readme_renderer",
            "tox",
        ],
        "tests": tests_require,
    },
    setup_requires=pytest_runner,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
)
