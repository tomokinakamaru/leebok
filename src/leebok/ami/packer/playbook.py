class Playbook(object):
    def __init__(self, config):
        self._config = config

    @property
    def content(self):
        return [{
            'name': 'Build AMI for AWS Parallel Cluster',
            'hosts': 'all',
            'become': True,
            'become_method': 'sudo',
            'tasks': self._tasks
        }]

    @property
    def _tasks(self):
        tasks = []

        if self._config.nvidia_driver_version is not None:
            tasks.extend(self._install_nvidia_driver)

        if self._config.cuda_version is not None:
            tasks.extend(self._install_cuda)

        if self._config.go_version is not None:
            tasks.extend(self._install_singularity)

        tasks.append(self._cleanup_ami)
        return tasks

    @property
    def _install_nvidia_driver(self):
        return [
            {
                'name': 'Download NVIDIA driver installer',
                'get_url': {
                    'url': self._nvidia_driver_installer_url,
                    'dest': '/tmp/nvidia.run'
                }
            },
            {
                'name': 'Run NVIDIA driver installer',
                'shell': 'sh nvidia.run -s',
                'args': {
                    'chdir': '/tmp'
                }
            },
            {
                'name': 'Remove NVIDIA driver installer',
                'file': {
                    'state': 'absent',
                    'path': ['/tmp/nvidia.run']
                }
            }
        ]

    @property
    def _install_cuda(self):
        return [
            {
                'name': 'Download CUDA installer',
                'get_url': {
                    'url': self._cuda_installer_url,
                    'dest': '/tmp/cuda.run'
                }
            },
            {
                'name': 'Run CUDA installer',
                'shell': 'sh cuda.run --silent --toolkit',
                'args': {
                    'chdir': '/tmp'
                }
            },
            {
                'name': 'Remove CUDA installer',
                'file': {
                    'state': 'absent',
                    'path': ['/tmp/cuda.run']
                }
            }
        ]

    @property
    def _install_singularity(self):
        return [
            self._install_singularity_dependencies,
            {
                'name': 'Install Go',
                'unarchive': {
                    'src': self._go_archive_url,
                    'dest': '/tmp',
                    'remote_src': 'yes'
                }
            },
            {
                'name': 'Download Singularity source',
                'unarchive': {
                    'src': self._singularity_source_url,
                    'dest': '/tmp',
                    'remote_src': 'yes'
                }
            },
            {
                'name': 'Generate Makefile for Singularity',
                'shell': './mconfig',
                'args': {'chdir': '/tmp/singularity'},
                'environment': {
                    'PATH': '/tmp/go/bin:{{ ansible_env.PATH }}'
                }
            },
            {
                'name': 'Build Singularity',
                'make': {'chdir': '/tmp/singularity/builddir'}
            },
            {
                'name': 'Install Singularity',
                'make': {
                    'target': 'install',
                    'chdir': '/tmp/singularity/builddir'
                }
            },
            {
                'name': 'Remove Go and Singularity source',
                'file': {
                    'state': 'absent',
                    'path': ['/tmp/go', '/tmp/singularity']
                }
            }
        ]

    @property
    def _install_singularity_dependencies(self):
        if self._config.os.startswith('centos'):
            return self._install_singularity_dependencies_centos
        if self._config.os.startswith('ubuntu'):
            return self._install_singularity_dependencies_ubuntu
        raise Exception(f'unsupported os: {self._config.os}')

    @property
    def _install_singularity_dependencies_centos(self):
        return {
            'name': 'Install Singularity dependencies',
            'yum': {
                'state': 'present',
                'name': [
                    '@Development Tools', 'cryptsetup',
                    'libseccomp-devel', 'libuuid-devel',
                    'openssl-devel', 'squashfs-tools', 'wget'
                ]
            }
        }

    @property
    def _install_singularity_dependencies_ubuntu(self):
        return {
            'name': 'Install Singularity dependencies',
            'apt': {
                'pkg': [
                    'build-essential', 'cryptsetup-bin', 'git',
                    'libgpgme-dev', 'libseccomp-dev', 'pkg-config',
                    'squashfs-tools', 'uuid-dev', 'wget'
                ]
            }
        }

    @property
    def _cleanup_ami(self):
        return {
            'name': 'Clean up AMI',
            'shell': 'sh ami_cleanup.sh',
            'args': {'chdir': '/usr/local/sbin'}
        }

    @property
    def _nvidia_driver_installer_url(self):
        return (
            'http://us.download.nvidia.com'
            f'/tesla/{self._config.nvidia_driver_version}'
            f'/NVIDIA-Linux-x86_64-{self._config.nvidia_driver_version}.run'
        )

    @property
    def _cuda_installer_url(self):
        cx, cy, cz = self._config.cuda_version.split('.')
        return (
            'http://developer.download.nvidia.com'
            f'/compute/cuda/{cx}.{cy}/Prod/local_installers'
            f'/cuda_{cx}.{cy}.{cz}'
            f'_{self._config.nvidia_driver_version}_linux.run'
        )

    @property
    def _go_archive_url(self):
        return (
            'https://dl.google.com'
            f'/go/go{self._config.go_version}.linux-amd64.tar.gz'
        )

    @property
    def _singularity_source_url(self):
        return (
            'https://github.com'
            '/sylabs/singularity/releases/download'
            f'/v{self._config.singularity_version}'
            f'/singularity-{self._config.singularity_version}.tar.gz'
        )
