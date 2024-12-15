from setuptools import setup, find_packages

# Read the contents of the README.md file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="comet_labs",  # Your package name
    version="0.1.4",
    description="A CLI tool for AI-driven commit messages and Jira integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sahil",
    author_email="sahil85.10s@gmail.com",
    packages=find_packages(),  # Automatically find all sub-packages
    install_requires=[
        "openai",
        "python-dotenv",
        "requests",
        "textblob>=0.17.1",
        # Add other dependencies here
    ],
    entry_points={
        "console_scripts": [
            "comet-labs=comet_labs.cli:main",  # Maps 'comet-labs' to the main() function in cli.py
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
