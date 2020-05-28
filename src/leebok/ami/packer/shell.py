import os
import platform
import stat
import subprocess
from urllib import request
from zipfile import ZipFile


class Shell(object):
    def __init__(self, config):
        self._config = config

    def run(self, *args):
        self._install()
        subprocess.check_call([self._path, *args])

    def _install(self):
        self._download_packer_zip()
        self._extract_packer()

    def _download_packer_zip(self):
        if not os.path.exists(self._zip_path):
            with request.urlopen(self._zip_url) as response:
                with open(self._zip_path, 'wb') as f:
                    f.write(response.read())

    def _extract_packer(self):
        if not os.path.exists(self._path):
            with ZipFile(self._zip_path).open('packer') as ef:
                with open(self._path, 'wb') as f:
                    f.write(ef.read())
        if not os.access(self._path, os.X_OK):
            os.chmod(self._path, os.stat(self._path).st_mode | stat.S_IEXEC)

    @property
    def _zip_url(self):
        return (
            'https://releases.hashicorp.com/packer'
            f'/{self._version}'
            f'/packer_{self._version}_{self._system}_{self._architecture}.zip'
        )

    @property
    def _zip_path(self):
        return os.path.join(self._workspace, f'packer{self._version}.zip')

    @property
    def _path(self):
        return os.path.join(self._workspace, f'packer{self._version}')

    @property
    def _system(self):
        return 'darwin' if platform.system() == 'Darwin' else 'linux'

    @property
    def _architecture(self):
        return 'amd64'

    @property
    def _workspace(self):
        return self._config.workspace

    @property
    def _version(self):
        return self._config.packer_version
