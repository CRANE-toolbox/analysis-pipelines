import pathlib

import setuptools

from os import path
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    README = f.read()
setuptools.setup(
    name="cranetoolbox",
    version="0.1.1", # Don't forget to also update docs/source/conf.py
    author="The CRANE Team",
    author_email="author@example.com",
    description="A package against racism around COVID-19",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/CRANE-toolbox/analysis-pipelines",
    packages=['cranetoolbox','cranetoolbox.importTools', 'cranetoolbox.analysis', 'cranetoolbox.preprocess'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": {
            "crane-import=cranetoolbox.importTools.__main__:main",
            "crane-analysis-quanti=cranetoolbox.analysis.__main__:main",
            "crane-preprocess=cranetoolbox.preprocess.__main__:main"
        }
    },
    python_requires='>=3.6',
    install_requires=['argparse', 'datetime', 'num2words', 'pathlib', 'pandas', 'typing', 'wordsegment'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-datafiles'],
)
