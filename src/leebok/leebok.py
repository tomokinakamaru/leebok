import shlex
import time
from cached_property import cached_property
from .config import Config
from .ami import AMI
from .pcluster import PCluster


class Leebok(object):
    def __init__(self):
        self.config = Config()

    def create(self):
        self.pcluster.create_config()
        self.pcluster.create()

    def submit(self):
        job = f'job{time.time()}.bash'
        for line in self._read(self.config.job):
            line = shlex.quote(line)
            self.pcluster.ssh(f"echo {line} >> {job}", capture_output=True)

        for args in self._read(self.config.job_args):
            self.pcluster.ssh(f'qsub {job} {args}')

    def status(self):
        self.pcluster.ssh('qstat')

    def ssh(self):
        self.pcluster.ssh()

    def delete(self):
        self.pcluster.delete()
        self.ami.delete()

    @cached_property
    def pcluster(self):
        return PCluster(self.config, self.ami.id)

    @cached_property
    def ami(self):
        return AMI(self.config)

    def _read(self, path):
        with open(path) as f:
            yield from (line.strip() for line in f)
