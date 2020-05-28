import os
from cached_property import cached_property
from pyparsing import alphanums, OneOrMore, Word
from urllib import request
from .ec2 import EC2
from .packer import Packer


class AMI(object):
    def __init__(self, config):
        self._config = config

    @cached_property
    def id(self):
        if not self._ec2.exists(self._config.name):
            Packer(self._config, self._source_ami).build()
        return self._ec2.find(self._config.name)

    def delete(self):
        if self._ec2.exists(self._config.name):
            self._ec2.delete(self._config.name)

    @cached_property
    def _ec2(self):
        return EC2(self._config.region)

    @cached_property
    def _source_ami(self):
        return self._source_amis[self._config.os][self._config.region]

    @cached_property
    def _source_amis(self):
        if not os.path.exists(self._source_ami_path):
            with request.urlopen(self._source_ami_url) as response:
                with open(self._source_ami_path, 'wb') as f:
                    f.write(response.read())
        return self._source_ami_parser.parseFile(self._source_ami_path)[0]

    @cached_property
    def _source_ami_path(self):
        name = f'amis{self._config.pcluster_version}.txt'
        return os.path.join(self._config.workspace, name)

    @cached_property
    def _source_ami_url(self):
        return (
            'https://raw.githubusercontent.com/aws/aws-parallelcluster'
            f'/v{self._config.pcluster_version}/amis.txt'
        )

    @cached_property
    def _source_ami_parser(self):
        chars = alphanums + '-'

        head = '#' + Word(chars)
        head.setParseAction(lambda pr: pr[-1])

        pair = Word(chars) + ':' + Word(chars)
        pair.setParseAction(lambda pr: (pr[0], pr[-1]))

        section = head + OneOrMore(pair)
        section.setParseAction(lambda pr: (pr[0], dict(pr[1:])))

        file = OneOrMore(section)
        file.setParseAction(lambda pr: dict(list(pr)))

        return file
