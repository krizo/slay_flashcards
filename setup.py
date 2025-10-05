from setuptools import setup, find_packages

setup(
    name="slayflashcards",
    version="1.0.0",
    description="An innovative flashcard application for enhanced learning",
    author="Krzysztof Bober",
    author_email="krizzb@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9.6",
    install_requires=[
        "typer>=0.9.0",
        "sqlalchemy>=2.0.0",
        "streamlit>=1.28.0",
        "gtts>=2.3.0",
        "pygame>=2.5.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "slayflashcards=cli.cli_application:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
