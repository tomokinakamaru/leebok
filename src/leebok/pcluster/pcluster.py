import os
from configparser import ConfigParser
from .shell import Shell


class PCluster(object):
    def __init__(self, config, custom_ami):
        self._config = config
        self._custom_ami = custom_ami
        self._shell = Shell(config)
        self._shell.install()

    def create_config(self):
        with open(self._config_path, 'w') as f:
            self._pcluster_config.write(f)

    def create(self):
        self._shell.pcluster(
            'create',
            '--config', self._config_path,
            self._config.name
        )

    def ssh(self, *args, capture_output=False):
        return self._shell.pcluster(
            'ssh', self._config.name,
            '-i', self._config.key_path,
            '-o', 'StrictHostKeyChecking no',
            *args,
            capture_output=capture_output)

    def delete(self):
        self._shell.pcluster('delete', self._config.name)
        os.remove(self._config_path)

    @property
    def _config_path(self):
        return os.path.join(self._config.workspace, f'{self._config.name}.ini')

    @property
    def _pcluster_config(self):
        config = ConfigParser()

        config['aws'] = {'aws_region_name': self._config.region}

        config['global'] = {
            'cluster_template': 'default',
            'sanity_check': 'true',
            'update_check': 'true'
        }

        config['aliases'] = {'ssh': 'ssh {CFN_USER}@{MASTER_IP} {ARGS}'}

        cluster = {
            'base_os': self._config.os,
            'compute_instance_type': self._config.compute_instance_type,
            'custom_ami': self._custom_ami,
            'key_name': self._config.key_name,
            'vpc_settings': 'default'
        }

        if self._config.compute_root_volume_size:
            cluster['compute_root_volume_size'] = (
                self._config.compute_root_volume_size
            )

        if self._config.master_instance_type:
            cluster['master_instance_type'] = (
                self._config.master_instance_type
            )

        if self._config.master_root_volume_size:
            cluster['master_root_volume_size'] = (
                self._config.master_root_volume_size
            )

        if self._config.s3_read_resource:
            cluster['s3_read_resource'] = (
                self._config.s3_read_resource
            )

        if self._config.s3_read_write_resource:
            cluster['s3_read_write_resource'] = (
                self._config.s3_read_write_resource
            )

        if self._config.spot_price or self._config.spot_bid_percentage:
            cluster['cluster_type'] = 'spot'

        if self._config.spot_price:
            cluster['spot_price'] = (
                self._config.spot_price
            )

        if self._config.spot_bid_percentage:
            cluster['spot_bid_percentage'] = (
                self._config.spot_bid_percentage
            )

        config['cluster default'] = cluster

        config['vpc default'] = {
            'master_subnet_id': self._config.master_subnet_id,
            'vpc_id': self._config.vpc_id
        }

        return config
