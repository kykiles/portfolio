from setuptools import setup, find_packages


setup(
    name='uparser',
    version='0.9.1',
    packages=find_packages(),
    description='Rutracker.org parser-downloader',
    author='Efimov Pavel',
    author_email='wowmanki@mail.ru',
    include_package_data=True,
    install_requires=[
        'Click',
        'lxml',
        'terminaltables',
        'requests'
    ],
    entry_points={
        'console_scripts': 'uparser=__init__:cli'
    }
)
