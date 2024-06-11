from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="hammy",
    version="0.0.7",
    description="optimization tool for building performance",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HammyTwoOfficial/hammy",
    author="YuxinQiuShuangyingXu",
    author_email="hammytwo.official@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["bson >= 0.5.10"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.7",
    package_data={
        "": ["**/*.pyd", "**/*.json", "**/*.pkl"],  # Recursively include all .pyd, .json, and .pkl files
    },
    include_package_data=True,  # Include package data as specified
)
