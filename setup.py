from setuptools import setup, find_packages

setup(
    name="comet_labs",
    version="0.1.1",
    description="AI-powered Git commit message generator with Jira integration.",
    packages=find_packages(),
    install_requires=["openai", "requests", "python-dotenv"],
    entry_points={"console_scripts": ["comet=comet.cli:main"]},
)
