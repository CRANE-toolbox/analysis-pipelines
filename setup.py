import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CRANE-Toolbox",
    version="0.0.1",
    author="The CRANE Team",
    author_email="author@example.com",
    description="A package against COVID-19",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CRANE-toolbox/analysis-pipelines",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
