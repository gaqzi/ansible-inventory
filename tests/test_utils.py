import os
from uuid import uuid4

import mock
import pytest

from ansible_inventory.utils import file_cache


def hello_factory():
    greetings = ['world']

    def hello():
        try:
            return {'saying': 'Hello {0}'.format(greetings.pop())}
        except IndexError:
            return {'saying': 'Good bye'}

    return hello

EXPECTED_GREETING = {'saying': 'Hello world'}
EXPECTED_GREETING_STRING = '{"saying": "Hello world"}'
EXPECTED_SECOND_GREETING = {'saying': 'Good bye'}
EXPECTED_SECOND_GREETING_STRING = '{"saying": "Good bye"}'


@pytest.fixture
def tempfile(request):
    filename = '/tmp/{0}.json'.format(uuid4())

    def remove_file():
        os.unlink(filename)

    request.addfinalizer(remove_file)

    return filename


def test_saves_wrapped_function_to_named_file():
    hello = hello_factory()
    assert hello() == {'saying': 'Hello world'}
    assert hello() == {'saying': 'Good bye'}


def test_should_save_output_to_file(tempfile):
    hello = file_cache(tempfile)(hello_factory())

    assert hello() == EXPECTED_GREETING
    assert open(tempfile).read() == EXPECTED_GREETING_STRING


def test_should_read_back_saved_response_from_file(tempfile):
    hello = file_cache(tempfile)(hello_factory())

    hello()
    assert os.path.exists(tempfile)
    assert hello() == EXPECTED_GREETING


def test_should_recreate_if_file_is_removed_between_reads(tempfile):
    hello = file_cache(tempfile)(hello_factory())

    hello()
    assert os.path.exists(tempfile)
    os.unlink(tempfile)
    assert not os.path.exists(tempfile)

    assert hello() == EXPECTED_SECOND_GREETING
    assert os.path.exists(tempfile)
    assert hello() == EXPECTED_SECOND_GREETING
    assert open(tempfile).read() == EXPECTED_SECOND_GREETING_STRING


def test_should_recall_wrapped_when_timeout_time_has_passed(tempfile):
    hello = file_cache(tempfile, timeout=300)(hello_factory())

    hello()
    assert os.path.exists(tempfile)
    mtime = os.path.getmtime(tempfile) - 301
    os.utime(tempfile, (mtime, mtime))

    assert hello() == EXPECTED_SECOND_GREETING
    assert open(tempfile).read() == EXPECTED_SECOND_GREETING_STRING


def test_should_only_read_back_from_filesystem_once(tempfile):
    hello = file_cache(tempfile)(hello_factory())
    with open(tempfile, 'w+') as f:
        f.write('1234')

    with mock.patch('ansible_inventory.utils.json.load') as m:
        m.return_value = 'Meeep'

        for x in range(10):
            assert hello() == 'Meeep'

        assert m.call_count == 1
