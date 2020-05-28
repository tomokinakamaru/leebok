import os
import subprocess
import sys
from urllib import request


class Shell(object):
    def __init__(self, config):
        self._config = config

    def install(self):
        self._download_virtualenv()
        self._download_getpip()
        self._create_venv()
        self._install_pip()
        self._install_pcluster()

    def pcluster(self, *args, capture_output=False):
        return self._execute(
            self._pcluster_path, *args, capture_output=capture_output)

    @property
    def pcluster_version(self):
        return self._config.pcluster_version

    def _download_virtualenv(self):
        if not os.path.exists(self._virtualenv_path):
            self._download(self._virtualenv_url, self._virtualenv_path)

    def _download_getpip(self):
        if not os.path.exists(self._getpip_path):
            self._download(self._getpip_url, self._getpip_path)

    def _create_venv(self):
        if not os.path.exists(self._venv_path):
            self._execute(
                sys.executable, self._virtualenv_path,
                self._venv_path, '--without-pip'
            )

    def _install_pip(self):
        if not os.path.exists(self._pip_path):
            self._execute(self._python_path, self._getpip_path)

    def _install_pcluster(self):
        if not os.path.exists(self._pcluster_path):
            self._execute(
                self._pip_path, 'install',
                f'aws-parallelcluster=={self._config.pcluster_version}'
            )

    def _download(self, url, path):
        with request.urlopen(url) as response:
            with open(path, 'wb') as file:
                file.write(response.read())

    def _execute(self, cmd, *args, capture_output=False):
        if capture_output:
            return subprocess.check_output([cmd, *args])
        else:
            return subprocess.check_call([cmd, *args])

    @property
    def _gitignore_path(self):
        return os.path.join(self._config.workspace, '.gitignore')

    @property
    def _virtualenv_url(self):
        return 'https://bootstrap.pypa.io/virtualenv.pyz'

    @property
    def _virtualenv_path(self):
        return os.path.join(self._config.workspace, 'virtualenv.pyz')

    @property
    def _getpip_url(self):
        return 'https://bootstrap.pypa.io/get-pip.py'

    @property
    def _getpip_path(self):
        return os.path.join(self._config.workspace, 'get-pip.py')

    @property
    def _venv_path(self):
        return os.path.join(
            self._config.workspace,
            f'venv{self._config.pcluster_version}')

    @property
    def _python_path(self):
        return os.path.join(self._venv_path, 'bin', 'python')

    @property
    def _pip_path(self):
        return os.path.join(self._venv_path, 'bin', 'pip')

    @property
    def _pcluster_path(self):
        return os.path.join(self._venv_path, 'bin', 'pcluster')
