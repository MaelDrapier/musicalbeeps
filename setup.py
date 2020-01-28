from setuptools import setup, find_packages

setup(
    name="musicalnotes",
    version="0.1.0",
    description="Play musical notes from command line or from your program",
    url="https://github.com/MaelDrapier/MusicalNotes",
    author="Maël Drapier",
    author_email="mael.drapier@gmail.com",
    keywords="music musical note notes play player sound frequency",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players"
    ],
    packages=find_packages(),
    install_requires=["pyaudio", "numpy"],
    entry_points={
        "console_scripts": [
            "musicalnotes=musicalnotes.script:main",
        ]
    },
)