import pathlib

import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setuptools.setup(
    name="cranetoolbox",
    version="0.0.0.9", # Don't forget to also update docs/conf.py
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
)
