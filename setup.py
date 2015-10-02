"""
Setup script.
"""

__version__ = '0.0.27'

from setuptools import setup, find_packages

if __name__ == '__main__':
    with \
            open('requirements.txt') as requirements, \
            open('test_requirements.txt') as test_requirements, \
            open('README.md') as readme:
        setup(
            name='aloe',
            version=__version__,
            description='Gherkin runner compatible with Lettuce',
            author='Alexey Kotlyarov',
            author_email='a@koterpillar.com',
            url='https://github.com/koterpillar/aloe',
            long_description=readme.read(),
            classifiers=[
                'License :: OSI Approved :: ' +
                'GNU General Public License v3 or later (GPLv3+)',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 3',
            ],

            packages=find_packages(exclude=['tests']),
            include_package_data=True,

            entry_points={
                'console_scripts': [
                    'aloe = aloe:main',
                ],
            },

            install_requires=requirements.readlines(),

            test_suite='tests',
            tests_require=test_requirements.readlines(),
        )
