import setuptools


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()


setuptools.setup(
    name="granitepy",
    version="0.2.0a",
    author="MrRandom#9258 and twitch 🔋#7443",
    url="https://github.com/iDevision/granitepy",
    licence="AGPL-3.0",
    description="A python client for the audio provider Andesite for use with discord.py.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['andesite', 'granitepy'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.6',
    classifiers=[
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet"
    ]
)
