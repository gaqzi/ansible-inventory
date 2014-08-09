import pytest

from ansible_inventory import Inventory
from ansible_inventory.exceptions import ImproperlyConfigured


@pytest.fixture
def inventory_hosts():
    return [
        dict(name='sedbpg01', ip_address='1.2.3.4', region_id=6,
             region_name='sgp1', hostname='generated-1-2-3-4.example.net',),
        dict(name='sedbpg02', ip_address='1.2.3.5', region_id=6,
             region_name='sgp1', hostname='generated-1-2-3-5.example.net',),
    ]


@pytest.fixture
def inventory_multiple_hosts_same_name():
    return [
        dict(name='sedbpg', ip_address='1.2.3.4', region_id=6,
             region_name='sgp1', hostname='generated-1-2-3-4.example.net',),
        dict(name='sedbpg', ip_address='1.2.3.5', region_id=6,
             region_name='sgp1', hostname='generated-1-2-3-5.example.net',),
    ]


@pytest.fixture()
def inventory(inventory_hosts):
    inventory = Inventory(data=inventory_hosts)
    inventory.address_field = 'ip_address'
    inventory.static = ['name']

    return inventory


def test_should_take_a_list_of_hosts(inventory_hosts):
    Inventory(data=inventory_hosts)


def test_should_be_able_to_return_a_static_field(inventory):
    hosts = inventory.json(dump=False)
    assert len(hosts) == 2
    assert 'sedbpg01' in hosts
    assert hosts['sedbpg01'] == ['1.2.3.4']


def test_should_be_able_to_return_several_static_fields(inventory):
    inventory.static = ['name', 'hostname']

    hosts = inventory.json(dump=False)
    assert len(hosts) == 4

    assert 'sedbpg01' in hosts
    assert hosts['sedbpg01'] == ['1.2.3.4']

    assert 'generated-1-2-3-4.example.net' in hosts
    assert hosts['generated-1-2-3-4.example.net'] == ['1.2.3.4']


def test_should_skip_fields_that_doesnt_exist(inventory):
    inventory.static = ['fizzbang']

    assert len(inventory.json(dump=False)) == 0


def test_should_let_the_address_field_be_configurable(inventory):
    inventory.address_field = 'hostname'

    hosts = inventory.json(dump=False)
    hostname = 'generated-1-2-3-4.example.net'

    assert len(hosts) == 2
    assert 'sedbpg01' in hosts
    assert hosts['sedbpg01'] == [hostname]


def test_should_raise_improperly_configuerd_when_no_address_field(inventory):
    inventory.address_field = None

    with pytest.raises(ImproperlyConfigured):
        inventory.json(dump=False)


def test_should_return_correct_number_of_addresses_for_hosts(inventory):
    inventory.data = inventory_multiple_hosts_same_name()

    hosts = inventory.json(dump=False)

    assert len(hosts) == 1
    assert 'sedbpg' in hosts

    assert len(hosts['sedbpg']) == 2
    assert hosts['sedbpg'] == ['1.2.3.4', '1.2.3.5']


def test_should_create_dynamic_groups_from_dynamic_functions(inventory):
    def country(self, host):
        return (host['name'][0:2], self.get_address(host))

    inventory.static = []
    inventory.dynamic = [country]

    hosts = inventory.json(dump=False)

    assert len(hosts) == 1
    assert 'se' in hosts
    assert hosts['se'] == ['1.2.3.4', '1.2.3.5']


def test_should_also_set_dynamic_from_class(inventory_hosts):
    class Inv(Inventory):
        dynamic = ['country']
        address_field = 'ip_address'

        def country(self, host):
            return (host['name'][0:2], self.get_address(host))

    inventory = Inv(data=inventory_hosts)
    hosts = inventory.json(dump=False)

    assert len(hosts) == 1
    assert 'se' in hosts
    assert hosts['se'] == ['1.2.3.4', '1.2.3.5']


def test_should_create_dynamic_group_from_template_strings(inventory):
    inventory.static = []
    inventory.static_template = ['region_{region_name}']

    hosts = inventory.json(dump=False)

    assert len(hosts) == 1
    assert 'region_sgp1' in hosts
    assert hosts['region_sgp1'] == ['1.2.3.4', '1.2.3.5']


def test_should_ignore_missing_keys_for_template_strings(inventory):
    inventory.static = []
    inventory.static_template = ['test_{nonexistant}']

    assert len(inventory.json(dump=False)) == 0
