"""
Setup script.
"""

from setuptools import setup, find_packages

with open('requirements.txt') as requirements, \
        open('test_requirements.txt') as test_requirements:
    setup(
        name='lychee',
        version='0.0.1',
        description='Gherkin runner compatible with Lettuce',
        author='Alexey Kotlyarov',
        author_email='a@koterpillar.com',
        url='https://github.com/koterpillar/lychee',
        long_description=open('README.md').read(),
        classifiers=[
            'License :: OSI Approved :: ' +
                'GNU General Public License v3 or later (GPLv3+)',
        ],

        packages=find_packages(exclude=['tests']),
        package_data={
            'lychee': [
                'README.md',
                'requirements.txt',
                'test_requirements.txt',
            ],
        },

        install_requires=requirements.read().splitlines(),

        test_suite='tests',
        tests_require=test_requirements.read().splitlines(),
    )
