import boto3
import inspect
import os
from cached_property import cached_property
from configparser import ConfigParser
from .ec2 import EC2
from .item import item


class Config(object):
    @item
    def workspace(self):
        return self._get('.leebok')

    @item
    def packer_version(self):
        return self._get('1.5.5')

    @item
    def pcluster_version(self):
        return self._get('2.6.1')

    @item
    def region(self):
        return self._get(boto3.Session().region_name or ERROR)

    @item
    def name(self):
        return self._get(ERROR)

    @item
    def key_name(self):
        return self._get(os.path.splitext(os.path.basename(self.key_path))[0])

    @item
    def key_path(self):
        return self._get(ERROR)

    @item
    def vpc_id(self):
        return self._get(self._ec2.find_vpc_id() or ERROR)

    @item
    def master_subnet_id(self):
        return self._get(self._ec2.find_subnet_id(self.vpc_id) or ERROR)

    @item
    def os(self):
        return self._get('centos7')

    @item
    def s3_read_resource(self):
        return self._get(None)

    @item
    def s3_read_write_resource(self):
        return self._get(None)

    @item
    def master_instance_type(self):
        return self._get(None)

    @item
    def master_root_volume_size(self):
        return self._get(None)

    @item
    def compute_instance_type(self):
        return self._get('g3s.xlarge' if self.cuda_version else 't2.micro')

    @item
    def compute_root_volume_size(self):
        return self._get(None)

    @item
    def spot_bid_percentage(self):
        return self._get(None)

    @item
    def spot_price(self):
        return self._get(None)

    @item
    def cuda_version(self):
        return self._get(None)

    @item
    def nvidia_driver_version(self):
        return self._get(None)

    @item
    def singularity_version(self):
        return self._get(None)

    @item
    def go_version(self):
        return self._get(None)

    @item
    def job(self):
        return self._get(ERROR)

    @item
    def job_args(self):
        return self._get(ERROR)

    @cached_property
    def _ec2(self):
        return EC2(self.region)

    def read(self, path):
        header = 'leebok'
        with open(path) as f:
            config = ConfigParser()
            config.read_string(f'[{header}]\n{f.read()}')
            for key, val in config[header].items():
                setattr(self, key, val)

    def _get(self, default):
        name = inspect.stack()[1][3]
        val = getattr(self, f'_{name}', UNSET)
        if val is UNSET:
            if default is ERROR:
                raise Exception(f'{name} is required')
            return default
        return val


UNSET = object()

ERROR = object()
