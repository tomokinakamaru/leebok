class Template(object):
    def __init__(self, config, source_ami, playbook_path):
        self._config = config
        self._source_ami = source_ami
        self._playbook_path = playbook_path

    @property
    def content(self):
        return {
            'builders': [
                {
                    'type': 'amazon-ebs',
                    'ami_name': self._ami_name,
                    'source_ami': self._source_ami,
                    'ssh_username': self._ssh_username,
                    'instance_type': self._instance_type,
                    'launch_block_device_mappings': (
                        self._launch_block_device_mappings
                    )
                }
            ],
            'provisioners': [
                {
                    'type': 'ansible',
                    'playbook_file': self._playbook_path
                }
            ]
        }

    @property
    def _ami_name(self):
        return f'{self._config.name}'

    @property
    def _ssh_username(self):
        if self._config.os.startswith('centos'):
            return 'centos'
        if self._config.os.startswith('ubuntu'):
            return 'ubuntu'
        raise Exception(f'unsupported os: {self._config.os}')

    @property
    def _instance_type(self):
        return self._config.compute_instance_type

    @property
    def _launch_block_device_mappings(self):
        if self._config.compute_root_volume_size is None:
            return []

        return [
            {
                'device_name': '/dev/sda1',
                'volume_size': str(self._config.compute_root_volume_size),
                'delete_on_termination': True
            }
        ]
