from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]
    # Remove comments from requirements
    requirements = [req.split("#")[0].strip() for req in requirements]

setup(
    name="ghost-blog-smart",
    version="1.0.16",  # Unified examples + simplified README with focus on features
    author="leowang.net",
    author_email="me@leowang.net",
    description="A powerful Python API for creating Ghost CMS blog posts with AI-powered features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/preangelleo/ghost-blog-smart",
    packages=find_packages(),
    package_data={
        "ghost_blog_smart": ["*.py"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "twine>=4.0",
            "wheel>=0.37",
            "setuptools>=65.0",
        ],
    },
    keywords="ghost cms blog ai gemini imagen markdown jwt api content-management",
    project_urls={
        "Bug Reports": "https://github.com/preangelleo/ghost-blog-smart/issues",
        "Source": "https://github.com/preangelleo/ghost-blog-smart",
        "Documentation": "https://github.com/preangelleo/ghost-blog-smart#readme",
    },
)
