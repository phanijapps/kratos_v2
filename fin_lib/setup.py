"""
Setup configuration for fin_lib - Professional Financial Analysis Library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fin_lib",
    version="1.0.0",
    author="Kratos Financial Tools",
    author_email="dev@kratos.ai",
    description="Professional financial analysis library for AI agents and quantitative analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kratos/fin_lib",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core financial data
        "yfinance>=0.2.18",
        "pandas>=1.5.0",
        "pandas-ta>=0.3.14b",
        "numpy>=1.21.0",
        
        # Professional charting
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "seaborn>=0.11.0",
        "mplfinance>=0.12.0",
        
        # Utilities
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fin-lib=fin_lib.cli:main",
        ],
    },
    keywords="finance, trading, stocks, forex, crypto, technical-analysis, fundamental-analysis, ai, agents",
    project_urls={
        "Bug Reports": "https://github.com/kratos/fin_lib/issues",
        "Source": "https://github.com/kratos/fin_lib",
        "Documentation": "https://fin-lib.readthedocs.io/",
    },
)
