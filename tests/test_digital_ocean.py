import json
from os import path

import mock
import pytest

from ansible_inventory.digital_ocean import DigitalOcean


def fixture_file(filename):
    return path.join(path.dirname(__file__), 'fixtures', filename)


@pytest.fixture()
def inventory(request, monkeypatch):
    monkeypatch.delenv('DO_API_KEY', raising=False)
    monkeypatch.delenv('DO_CLIENT_ID', raising=False)

    m = mock.patch('ansible_inventory.digital_ocean.DoManager')
    DoManager = m.start()
    instance = DoManager()
    instance.all_active_droplets.return_value = json.load(
        open(fixture_file('digital_ocean/hosts.json'))
    )
    instance.all_regions.return_value = json.load(
        open(fixture_file('digital_ocean/regions.json'))
    )
    instance.all_images.return_value = json.load(
        open(fixture_file('digital_ocean/images.json'))
    )
    instance.all_ssh_keys.return_value = json.load(
        open(fixture_file('digital_ocean/ssh_keys.json'))
    )
    instance.sizes.return_value = json.load(
        open(fixture_file('digital_ocean/sizes.json'))
    )
    request.addfinalizer(m.stop)

    inventory = DigitalOcean(fixture_file('digital_ocean.ini'))

    return inventory


def test_should_use_configuration(inventory):
    assert inventory.config.get('api_key') == '123456abcdefg'


def test_should_be_able_get_all_hosts_from_backend(inventory):
    assert len(inventory.get_data()) == 5


def test_should_mimic_the_standard_ansible_do_inventory(inventory):
    hosts = inventory.json(dump=False)
    for k in hosts.keys():
        print k

    assert 1397172 in hosts
    assert 'status_active' in hosts

    assert 'region_6' in hosts
    assert 'region_sgp1' in hosts

    assert 'size_66' in hosts
    assert 'size_512mb' in hosts

    assert 'image_3101045' in hosts
    assert 'image_ubuntu-12-04-x64' in hosts
