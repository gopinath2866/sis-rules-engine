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
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-hcl2>=0.3.0",
        "PyYAML>=6.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "sis=sis.cli:main",
        ],
    },
    include_package_data=True,
    keywords="security, terraform, kubernetes, docker, cloudformation, devsecops",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sis/issues",
        "Source": "https://github.com/yourusername/sis",
        "Documentation": "https://github.com/yourusername/sis/docs",
    },
)
