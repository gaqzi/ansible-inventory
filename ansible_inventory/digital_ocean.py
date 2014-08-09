from dopy.manager import DoManager

from . import Inventory
from .config import Settings
from .utils import file_cache


class DigitalOceanBase(Inventory):
    address_field = 'ip_address'

    def __init__(self, settings_file='digital_ocean.ini'):
        super(DigitalOceanBase, self).__init__()

        self.config = Settings(prefix='DO', section='digital_ocean',
                               filename=settings_file)
        self.data_params = {}
        self.do = DoManager(self.config.get('client_id'),
                            self.config.get('api_key'))

    @file_cache('/tmp/ansible-droplets-cache.json')
    def get_data(self):
        if not self.data:
            self.data = self.do.all_active_droplets()

        return self.data

    @file_cache('/tmp/ansible-data-params-cache.json', timeout=3600)
    def get_data_params(self):
        if not self.data_params:
            def _convert(data):
                ret = {}
                for datum in data:
                    # Ensure keys are always strings because JSON
                    # strings are always strings
                    ret[str(datum['id'])] = datum

                return ret

            self.data_params['regions'] = _convert(self.do.all_regions())
            self.data_params['images'] = _convert(self.do.all_images())
            self.data_params['ssh_keys'] = _convert(self.do.all_ssh_keys())
            self.data_params['sizes'] = _convert(self.do.sizes())

        return self.data_params

    def get_data_param(self, host, part, find_key, display_template):
        try:
            datum = self.get_data_params()[part][str(host[find_key])]
        except KeyError:
            pass
        else:
            return (display_template.format(**datum), self.get_address(host))


class DigitalOcean(DigitalOceanBase):
    static = ['id', 'name', 'hostnames']
    static_template = ['region_{region_id}', 'status_{status}',
                       'size_{size_id}', 'image_{image_id}']
    dynamic = ['region_name', 'size_name', 'image_name']

    def region_name(self, host):
        return self.get_data_param(host, 'regions', 'region_id',
                                   'region_{slug}')

    def size_name(self, host):
        return self.get_data_param(host, 'sizes', 'size_id', 'size_{slug}')

    def image_name(self, host):
        return self.get_data_param(host, 'images', 'image_id', 'image_{slug}')
