from distutils.core import setup

setup(
    name = 'vsdnagent',
    version = '0.1',
    packages = ['vsdnagent'],
    url = 'https://github.com/FernandoFarias/vsdnagent',
    license = 'Apache2',
    author = 'Fernando Farias',
    author_email = 'fernnf@gmail.com',
    description = '',
    requires = ['pyroute2', 'docker', 'cmd2', 'requests', 'names']
)

