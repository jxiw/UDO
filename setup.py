from distutils.core import setup

setup(
    name='UDO',  # How you named your package folder (MyLib)
    packages=['UDO'],  # Chose the same as "name"
    version='0.01',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='a universal optimizer for database system',  # Give a short description about your library
    author='Junxiong Wang',  # Type in your name
    author_email='junxiong@cs.cornell.edu',  # Type in your E-Mail
    url='https://ovss.github.io/UDO/',  # Provide either the link to your github or to your website
    download_url='https://github.com/OVSS/UDO/archive/refs/tags/0.01.tar.gz',  # I explain this later on
    keywords=['Database Optimization', 'OLAP', 'Index selection', 'System parameters'],
    # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'numpy>=1.19.5',
        'testresources>=2.0.1',
        'gym>=0.17.3',
        'tensorflow>=2.4.1',
        'keras>=2.4.3',
        'keras-rl>=0.4.2',
        'mysqlclient>=2.0.3',
        'psycopg2>=2.8.6'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
