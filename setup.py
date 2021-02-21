from setuptools import setup


with open('README.md', 'r') as fh:
	long_description = fh.read()

setup(
	name='contextlogger',
	version='1.0.1',
	description='A logging boilerplate enhanced by the use of contextvars',
	url='https://github.com/kolitiri/contextlogger',
	author='Christos Liontos',
	license='MIT',
	classifiers=[
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	keywords='logging context',
	project_urls={
		'Source': 'https://github.com/kolitiri/contextlogger',
		'Tracker': 'https://github.com/kolitiri/contextlogger/issues',
	},
	py_modules=['contextlogger', 'exceptions'],
	package_dir={'': 'src'},
	long_description=long_description,
	long_description_content_type='text/markdown',
	extras_require={
		"dev": [
			"pytest>=3.7",
		],
	}
)
