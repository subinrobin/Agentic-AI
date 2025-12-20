from setuptools import setup, find_packages

setup(
    name="ai_agents",
    version="0.1.0",
    description="Enterprise-grade Python project for intelligent agent development.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.8",
)
