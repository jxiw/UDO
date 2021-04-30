from setuptools import setup, find_packages

setup(name='udo_db',
      version='0.18',
      description='a universal optimizer for database system',
      author='Junxiong Wang',
      author_email='chuangzhetianxia@gmail.coma',
      url='https://ovss.github.io/UDO/',
      download_url='https://github.com/OVSS/UDO/archive/refs/tags/0.01.tar.gz',
      keywords=['Database Optimization', 'OLAP', 'Index selection', 'System parameters'],
      packages=find_packages(),
      license='MIT',
      install_requires=[  # I get to this in a second
          'numpy==1.19.2',
          'h5py==2.10.0',
          'testresources>=2.0.1',
          'gym>=0.17.3',
          'udo_optimization>=0.0.2',
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
      ])
