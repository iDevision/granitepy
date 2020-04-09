import setuptools


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md") as f:
    readme = f.read()


setuptools.setup(
    name="granitepy",
    author="MrRandom#9258 and twitch 🔋#7443",
    version="0.4.1",
    url="https://github.com/iDevision/granitepy",
    packages=setuptools.find_packages(),
    licence="MIT",
    description="A python client for the audio provider Andesite for use with discord.py.",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extra_require=None,
    classifiers=[
        "Framework :: AsyncIO",
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        "Topic :: Internet"
    ],
    python_requires='>=3.6',
    keywords=['andesite', 'granitepy', "discord.py"],
)
