from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name = 'vsdnemul',
      version = '0.2',
      long_description = readme(),
      packages = find_packages(),
      url = 'https://github.com/FernandoFarias/vsdnemul',
      classifiers = [
          'Development Status :: 0.2 - Release',
          'License :: OSI Approved :: APACHE2 License',
          'Programming Language :: Python :: 3.6',
          'Topic :: SDN Develop :: Network Emulator',
      ],
      license = 'Apache2',
      author = 'Fernando Farias',
      author_email = 'fernnf@gmail.com',
      description = 'A SDN topology emulator to create specific topologies for research and development in SDN',
      keywords = "SDN Networking Emulator",
      install_requires = ['pyroute2', 'docker', 'cmd2', 'requests', 'names', 'ryu', 'terminaltables'],
      include_package_data = True,
      zip_safe = False)
