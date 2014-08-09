import json

from .exceptions import ImproperlyConfigured


class InventoryBase(object):
    address_field = None
    static = []
    static_template = []
    dynamic = []
    data = None

    def __init__(self, **kwargs):
        self.data = kwargs.get('data', None)
        self.inventory = {}

    def get_data(self):
        if self.data is None:
            raise ImproperlyConfigured(
                'InventoryBase requires either a list of host data in '
                '"data" or an implementation of "get_data()"'
            )

        return self.data

    def push(self, key, address):
        try:
            self.inventory[key].append(address)
        except KeyError:
            self.inventory[key] = []
            self.push(key, address)

    def get_address_field(self):
        if not self.address_field:
            raise ImproperlyConfigured(
                'InventoryBase requires either a definition of '
                '"address_field" or an implementation of '
                '"get_address_field()"'
            )

        return self.address_field

    def get_address(self, host):
        return host.get(self.get_address_field())

    def set_static(self, host):
        """Create a group from a key on a ``host``.

        Args:
          host (dict): A host definition

        Returns:
          list: (`group_name`, `server_address`)
        """
        for field in self.static:
            try:
                self.push(host[field], self.get_address(host))
            except KeyError:
                pass

    def set_static_template(self, host):
        """Convert a :func:`str.format` string to a group by interpolating it
        with the keys from a ``host``

        Args:
          host (dict): A host definition

        Returns:
          list: (`group_name`, `server_address`)

        """
        for field in self.static_template:
            try:
                self.push(field.format(**host), self.get_address(host))
            except KeyError:
                pass

    def set_dynamic(self, host):
        """Create a host group by calling a function/method with a host
        definition.

        For instance, you have a naming scheme and want to have groups
        automatically created based off of that scheme. Example: the
        first two letters of a hostname refers to the country where
        the server is located. And you would like to have a dynamic
        group made from those hosts.

        Example::

            def country_group(self, host):
                return (host['name'][0:2], self.get_address(host))

            dynamic = [country_group]

        Args:
          host (dict): A host definition

        Returns:
          list: (`group_name`, `server_address`)

        """
        for dynamic in self.dynamic:
            if hasattr(dynamic, '__call__'):
                val = dynamic(self, host)
            elif hasattr(self, dynamic):
                val = getattr(self, dynamic)(host)

            if val:
                self.push(*val)

    def _set_inventory_from_data(self):
        for host in self.get_data():
            self.set_static(host)
            self.set_static_template(host)
            self.set_dynamic(host)

    def json(self, dump=True):
        self._set_inventory_from_data()

        if dump:
            return json.dumps(self.inventory)
        else:
            return self.inventory


class Inventory(InventoryBase):
    pass
