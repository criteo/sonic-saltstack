#!/usr/bin/env python3

import setuptools
import os


def _read_reqs(relpath):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    with open(fullpath) as f:
        return [s.strip() for s in f.readlines() if (s.strip() and not s.startswith("#"))]


setuptools.setup(
    name="sonic-salt",
    version="1.0",
    include_package_data=True,
    tests_require=_read_reqs("tests-requirements.txt"),
    dependency_links=[],
    packages=setuptools.find_packages(),
)
