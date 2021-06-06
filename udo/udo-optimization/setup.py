from setuptools import setup, find_packages

setup(
    name='udo_optimization',
    version='0.0.3',
    description='gym environment for UDO',
    author='Junxiong Wang',
    author_email='chuangzhetianxia@gmail.coma',
    url='https://ovss.github.io/udo_optimization/',
    install_requires=['gym>=0.17.3'],
    packages=find_packages()
)
