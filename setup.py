import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

install_requires = ['silabeador', 'stanza']


# This call to setup() does all the work
setup(
    name="libEscansion",
    version="1.0.0-5",
    python_requires='>=3.5',
    description="Metrical scansion for Spanish verses",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/fsanzl/libEscansion",
    project_urls={
        'Source': 'https://github.com/fsanzl/libEscansion/',
        'Tracker': 'https://github.com/fsanzl/libEscansion/issues',
    },
    author="Fernando Sanz-Lázaro",
    author_email="fsanzl@gmail.com",
    license="LGPL",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General "
        "Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Natural Language :: Spanish",
    ],
    packages=find_packages(include=['libEscansion', 'libEscansion.*'])
)
    #include_package_data=True,
    #entry_points={
    #    "console_scripts": [
    #        "libEscansion=libEscansion.__main__:main",
    #    ]
    #},

