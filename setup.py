from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="oddspipe",
    version="0.4.0",
    description="Python client for the OddsPipe prediction market API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OddsPipe",
    author_email="hello@oddspipe.com",
    url="https://oddspipe.com",
    project_urls={
        "Documentation": "https://oddspipe.com/docs",
        "Source": "https://github.com/OddsPipe/oddspipe-python",
    },
    packages=find_packages(),
    install_requires=["httpx"],
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial",
    ],
)
