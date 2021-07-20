import hamcrest
from unittest.mock import Mock
from typing import Literal
import reiter.arango.binding
from uvcreha import events
from uvcreha.contenttypes import registry, CRUD


def test_contenttype_crud(uvcreha):

    user_type = registry['user']
    db = uvcreha.utilities['arango']
    bind = user_type.bind(db.get_database())

    assert isinstance(bind, reiter.arango.binding.Binder) is True
    crud = CRUD(uvcreha, bind)

    witness = Mock()

    @uvcreha.subscribers.subscribe(events.ObjectEvent)
    def something_happened(event):
        witness(event)

    res = crud.create(data = dict(
        uid="1234567",
        loginname="souheil",
        password="secret",
        email="trollfot@gmail.com"
    ))

    witness.assert_called_once()
    event = witness.call_args.args[0]
    assert isinstance(event, events.ObjectCreatedEvent)
    witness.reset_mock()

    assert res['uid'] == "1234567"
    assert res['uid'] ==  bind.find_one(uid='1234567')['uid']

    res = crud.update(res, {'email': 'ck@novareto.de'})
    assert bind.find_one(uid='1234567')['email'] == 'ck@novareto.de'
    witness.assert_called_once()
    event = witness.call_args.args[0]
    assert isinstance(event, events.ObjectModifiedEvent)
    witness.reset_mock()

    res = bind.find_one(uid='1234567')
    res = crud.delete(res)
    assert bind.find_one(uid='1234567') is None
    witness.assert_called_once()
    event = witness.call_args.args[0]
    assert isinstance(event, events.ObjectRemovedEvent)
