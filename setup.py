from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sis-security-scanner",
    version="1.0.0",
    author="SIS Security",
    author_email="contact@sis-security.com",
    description="Security scanner for infrastructure-as-code (Terraform, Kubernetes, Docker, CloudFormation)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "python-hcl2>=0.3.0",
        "PyYAML>=6.0",
        "colorama>=0.4.6",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "sis=sis.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
