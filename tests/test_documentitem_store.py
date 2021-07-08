import pytest
from uvcreha.jsonschema import DocumentItemStore, VersionedValue, Version


def test_empty_versioned_value():
    vv = VersionedValue()
    assert vv.latest == 0
    assert len(vv) == 0
    assert bool(vv) is False

    with pytest.raises(KeyError):
        vv.get(0)

    with pytest.raises(KeyError):
        vv.get()

    with pytest.raises(KeyError):
        vv.remove(0)


def test_version_keys():
    vv = VersionedValue()

    # Failed type casting
    with pytest.raises(ValueError):
        vv.add('john', 'a')

    # Value verification
    with pytest.raises(AssertionError) as exc:
        vv.add('john', 0)
    assert str(exc.value) == 'Version number must be positive and non-null.'

    with pytest.raises(AssertionError) as exc:
        vv.add('john', -1)
    assert str(exc.value) == 'Version number must be positive and non-null.'

    # Type casting
    num = vv.add('john', '1')
    assert num == 1


def test_versioned_value():
    vv = VersionedValue()
    version_number = vv.add('john')
    assert version_number == 1
    assert vv.latest == 1
    assert bool(vv) == True

    with pytest.raises(KeyError):
        vv.get(0)

    version = vv.get()
    assert version.number == 1
    assert version.value == 'john'

    with pytest.raises(ValueError) as exc:
        version_number = vv.add('jane', 1)
    assert str(exc.value) == "Version 1 already exists."

    version_number = vv.add('jane', 2)
    assert vv.latest == 2
    assert len(vv) == 2
    version = vv.get()
    assert version.number == 2
    assert version.value == 'jane'

    version = vv.get(1)
    assert version.number == 1
    assert version.value == 'john'

    vv.remove(2)
    assert vv.latest == 1
    version = vv.get()
    assert version.number == 1
    assert version.value == 'john'

    version = vv.remove(1)  # removal returns the removed version/value
    assert version.number == 1
    assert vv.latest == 0
    assert bool(vv) == False
    assert len(vv) == 0


def test_document_item_store():
    items = DocumentItemStore()

    assert bool(items) is False
    assert 'unknown' not in items
    assert items.get('unknown') is None
    assert items.get('unknown', 0) is None

    with pytest.raises(KeyError):
        items.remove('unknown')

    num = items.add('known', 'john')
    assert num == 1
    assert len(items) == 1
    assert bool(items) is True
    assert 'known' in items

    items.remove('known')
    assert len(items) == 0
    assert bool(items) is False
    assert 'known' not in items

    num = items.add('name', 'jane')
    assert num == 1
    assert len(items) == 1
    assert bool(items) is True
    assert 'name' in items

    version = items.get('name')
    assert version.number == 1
    assert version.value == 'jane'

    with pytest.raises(KeyError):
        items.get('name', version=2)

    num = items.add('name', 'john')
    assert num == 2
    assert len(items) == 1

    version = items.get('name', version=2)
    assert version == items.get('name')
    assert version.number == 2
    assert version.value == 'john'

    items.remove('name', version=1)
    with pytest.raises(KeyError):
        items.get('name', version=1)

    version = items.get('name')
    assert version.value == 'john'
