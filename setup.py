from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name = "MLOps-Project-01",
    version = "1.0",
    author = "Amasha",
    packages = find_packages(),
    install_requires = requirements
)



