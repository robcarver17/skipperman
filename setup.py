from __future__ import print_function
import os
import sys
import platform
from setuptools import setup, find_packages
from distutils.version import StrictVersion

if StrictVersion(platform.python_version()) <= StrictVersion("3.7.0"):
    print("skipperman requires Python 3.7.0 or later. Exiting.", file=sys.stderr)
    sys.exit(1)


def read(fname):
    """Utility function to read the README file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def package_files(directory, extension="yaml"):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.split(".")[-1] == extension:
                paths.append(os.path.join("..", path, filename))

    return paths


def dir_this_file():
    return os.path.dirname(os.path.realpath(__file__))


data_csv_path = os.path.join(dir_this_file(), "example_data")
data_csv_files = package_files(data_csv_path, "csv")


package_data = {
    "":data_csv_files
}

print(package_data)

setup(
    name="skipperman",
    version="0.0.1",
    author="Robert Carver",
    description=(
        "BSC cadet management system"
    ),
    license="GNU GPL v3",
    keywords="sailing wildapricot",
    url="https://github.com/robcarver17/skipperman",
    packages=find_packages(),
    package_data=package_data,
    long_description=read("README.md"),
    install_requires=[
        "pandas==1.0.5",
    ],
    tests_require=["nose", "flake8"],
    extras_require=dict(),
    test_suite="nose.collector",
    include_package_data=True,
)
