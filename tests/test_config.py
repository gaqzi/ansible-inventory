from os import path

import pytest

from ansible_inventory.config import (
    EnvironmentSettings,
    IniSettings,
    Settings,
)


@pytest.fixture
def settings():
    return Settings(prefix='DO', section='digital_ocean',
                    filename=path.join(path.dirname(__file__),
                                       'fixtures/digital_ocean.ini'))


@pytest.fixture
def ini_settings():
    return IniSettings(section='digital_ocean',
                       filename=path.join(path.dirname(__file__),
                                          'fixtures/digital_ocean.ini'))


@pytest.fixture
def env_settings():
    return EnvironmentSettings(prefix='DO')


def test_reads_settingsuration_key_from_ini(ini_settings):
    assert ini_settings.get('client_id') == 'abcdefg123456'


def test_reads_non_existant_key_from_ini_returns_none(ini_settings):
    assert ini_settings.get('nonexistant') is None


def test_reads_settingsuration_key_from_env(env_settings, monkeypatch):
    val = 'abcdefg123456'
    monkeypatch.setenv('DO_CLIENT_ID', val)

    assert env_settings.get('client_id') == val


def test_reads_non_existant_key_from_env_returns_none(env_settings,
                                                      monkeypatch):
    monkeypatch.delenv('DO_NONEXISTANT', raising=False)

    assert env_settings.get('nonexistant') is None


def test_settings_should_read_env_first(settings, monkeypatch):
    monkeypatch.setenv('DO_CLIENT_ID', 'hello')

    assert settings.get('client_id') == 'hello'


def test_settings_should_fallback_to_ini_when_nothing_in_env(settings,
                                                             monkeypatch):
    monkeypatch.delenv('DO_CACHE_MAX_AGE', raising=False)

    assert settings.get('cache_max_age') == '300'


def test_settings_should_return_none_when_nothing_anywhere(settings,
                                                           monkeypatch):
    monkeypatch.delenv('DO_NONEXISTANT', raising=False)

    assert settings.get('nonexistant') is None
