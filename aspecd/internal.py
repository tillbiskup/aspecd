import os
import sys
import platform
import getpass


__packagename__ = 'aspecd'
__filepath__ = os.path.dirname(__file__)


def version():
    version_filepath = os.path.join(__filepath__, '..', 'VERSION')
    with open(version_filepath) as version_file:
        version = version_file.read().strip()
    return version


def config_dir():
    config_dir = os.environ.get(
        'XDG_CONFIG_HOME',
        os.path.join(os.path.expanduser('~'), '.config')
        )
    return config_dir


def _package_name():
    return __packagename__


def info():
    info = {
            'name': _package_name(),
            'version': version(),
            'python': sys.version,
            'platform': platform.platform(),
            'user': getpass.getuser()
            }
    return info


# if __name__ == "__main__":
#    print('Version: {}'.format(version()))
#    print('Confdir: {}'.format(config_dir()))
