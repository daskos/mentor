from __future__ import absolute_import, division, print_function

from mentor.utils import remote_exception


def test_remote_exception():
    e = TypeError("hello")
    a = remote_exception(e, 'traceback')
    b = remote_exception(e, 'traceback')

    assert type(a) == type(b)
    assert isinstance(a, TypeError)
    assert 'hello' in str(a)
    assert 'traceback' in str(a)
