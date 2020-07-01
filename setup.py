from setuptools import setup
import memsource


def parse_requirements():
    with open('requirements.txt') as f:
        return [l.strip() for l in f.readlines() if not l.startswith('#')]


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='Memsource-wrap',
    version=memsource.__version__,
    description=readme(),
    license=memsource.__license__,
    author=memsource.__author__,
    author_email='devops@gengo.com',
    url='https://github.com/gengo/memsource-wrap',
    keywords='Memsource API',
    packages=('memsource', 'memsource.lib', 'memsource.api_rest'),
    install_requires=parse_requirements(),
)
