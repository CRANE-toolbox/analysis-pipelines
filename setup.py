import pathlib

import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setuptools.setup(
    name="cranetoolbox",
    version="0.0.0.6",
    author="The CRANE Team",
    author_email="author@example.com",
    description="A package against racism around COVID-19",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/CRANE-toolbox/analysis-pipelines",
    packages=['cranetoolbox','cranetoolbox.importTools'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": {
            "crane-import=cranetoolbox.importTools.__main__:main"
        }
    },

    install_requires=["nltk>=3.5",
                      "pandas>=1.1.0",
                      "requests>=2.24",
                      "num2words>=0.5.10",
                      "ratelimit>=2.2.1",
                      "gensim>=3.8.3",
                      "wordsegment>=1.3",
                      "sphinx>=3",
                      ],
    python_requires='>=3.6',
)
