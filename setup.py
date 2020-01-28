from setuptools import setup, find_packages

setup(
    name="musicalnotes",
    version="0.1.0",
    description="Play musical notes from command line or from your program",
    url="https://github.com/MaelDrapier/MusicalNotes",
    author="Maël Drapier",
    author_email="mael.drapier@gmail.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "musicalnotes=musicalnotes.script:main",
        ]
    },
)