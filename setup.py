#!/usr/bin/env python
from codecs import open
from setuptools import setup

from gtbump import __version__

README = open("README.md").read()

setup(
	name="gtbump",
	version=__version__,
	description="git-tag-bump: a simple utility for quickly bumping Git semver tags",
	long_description=README,
	long_description_content_type="text/markdown",
	author="Kailash Nadh",
	author_email="kailash@nadh.in",
	url="https://github.com/knadh/gtbump",
	packages=['gtbump'],
	include_package_data=True,
	download_url="https://github.com/knadh/gtbump",
	license="MIT License",
	entry_points={
		'console_scripts': [
			'gtbump = gtbump:main'
		],
	},
	classifiers=[
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Build Tools"
	]
)
