from setuptools import setup


with open("README.md") as fh:
    long_description = fh.read()


setup(
    name="granitepy",
    packages=['granitepy'],
    version="0.1.0a",
    description="An async library for the lavalink like audio provider called andesite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="twitch#7443 and MrRandom#9258",
    url="https://github.com/iDevision/granitepy",
    keywords=['andesite', 'granitepy'],
    install_requires=['aiohttp', 'discord.py'],
    classifiers=[
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet"
    ]
)
