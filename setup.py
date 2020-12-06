from setuptools import setup


with open('README.md', 'r') as fh:
	long_description = fh.read()

setup(
	name='contextlogger',
	version='0.0.5',
	description='A logging boilerplate enhanced by the use of contextvars',
	py_modules=['contextlogger', 'exceptions'],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	long_description=long_description,
	long_description_content_type='text/markdown',
	extras_require={
		"dev": [
			"pytest>=3.7",
		],
	}
)
