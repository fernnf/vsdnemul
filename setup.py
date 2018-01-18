from distutils.core import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name = 'vsdnagent',
      version = '0.1',
      long_description = readme(),
      packages = ['vsdnagent'],
      url = 'https://github.com/FernandoFarias/vsdnagent',
      classifiers = [
          'Development Status :: 0.1 - Release',
          'License :: OSI Approved :: APACHE2 License',
          'Programming Language :: Python :: 3.6',
          'Topic :: SDN Develop :: Network Emulator',
      ],
      license = 'Apache2',
      author = 'Fernando Farias',
      author_email = 'fernnf@gmail.com',
      description = 'A SDN topology emulator to create specific topologies for research and development in SDN',
      install_requires = ['pyroute2', 'docker', 'cmd2', 'requests', 'names'],
      include_package_data = True,
      zip_safe = False)
