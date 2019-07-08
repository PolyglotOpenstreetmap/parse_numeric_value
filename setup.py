import setuptools
import setuptools.command.install
from pathlib import Path

class PostInstallCommand(setuptools.command.install.install):
    """Post-installation command."""
    def run(self):
        setuptools.command.install.install.run(self)
        try:
            import spacy
            spacy.cli.validate()
        except ModuleNotFoundError:
            pass


with open(Path(__file__).resolve().parent.joinpath('README.md'), 'r') as fh:
    long_description = fh.read()

with open(Path(__file__).resolve().parent.joinpath('requirements.txt'), 'r') as fh:
    requirements = [r.split('#', 1)[0].strip() for r in fh.read().split('\n')]

with open(Path(__file__).resolve().parent.joinpath('VERSION'), 'r') as fh:
    version = fh.read()

setuptools.setup(
    name='parse_numeric_value',
    version=version,
    description='parse_numeric_value: convert text to its numeric value',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PolyglotOpenstreetmap/parse_numeric_value',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GPL3 License',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    cmdclass={
        'install': PostInstallCommand,
    },
)