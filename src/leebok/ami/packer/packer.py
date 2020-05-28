import json
import os
import time
import yaml
from .playbook import Playbook
from .shell import Shell
from .template import Template


class Packer(object):
    def __init__(self, config, source_ami):
        self._config = config
        self._source_ami = source_ami
        self._timestamp = time.time()

    def build(self):
        self._create_playbook()
        self._create_template()
        Shell(self._config).run('build', self._template_path)
        self._delete_playbook()
        self._delete_template()

    def _create_template(self):
        t = Template(self._config, self._source_ami, self._playbook_path)
        with open(self._template_path, 'w') as f:
            json.dump(t.content, f)

    def _create_playbook(self):
        p = Playbook(self._config)
        with open(self._playbook_path, 'w') as f:
            yaml.dump(p.content, f)

    def _delete_template(self):
        os.remove(self._template_path)

    def _delete_playbook(self):
        os.remove(self._playbook_path)

    @property
    def _template_path(self):
        return os.path.join(self._workspace, self._template_name)

    @property
    def _playbook_path(self):
        return os.path.join(self._workspace, self._playbook_name)

    @property
    def _template_name(self):
        return f'{self._timestamp}.json'

    @property
    def _playbook_name(self):
        return f'{self._timestamp}.yml'

    @property
    def _workspace(self):
        return self._config.workspace
