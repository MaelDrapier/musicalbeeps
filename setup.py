import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "PYPI_README.md").read_text()

setup(
    name="MusicalBeeps",
    version="0.2.8",
    description="Play sound beeps corresponding to musical notes.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/MaelDrapier/MusicalBeeps",
    author="Maël Drapier",
    author_email="mael.drapier@gmail.com",
    license="MIT",
    keywords="music musical note notes beep beeps play player sound frequency",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players"
    ],
    packages=find_packages(),
    install_requires=["numpy", "simpleaudio"],
    entry_points={
        "console_scripts": [
            "musicalbeeps=musicalbeeps.script:main",
        ]
    },
)