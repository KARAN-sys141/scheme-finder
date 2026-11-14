import threading
import time
import uuid
from collections import OrderedDict

MAX_SESSIONS = 1000
TTL_SECONDS = 3600

_store = OrderedDict()
_lock = threading.Lock()


def new_id():
    return uuid.uuid4().hex


def get(session_id):
    with _lock:
        item = _store.get(session_id)
        if not item:
            return {}
        if time.time() - item["t"] > TTL_SECONDS:
            _store.pop(session_id, None)
            return {}
        return dict(item["state"])


def put(session_id, state):
    with _lock:
        _store[session_id] = {"state": state, "t": time.time()}
        _store.move_to_end(session_id)
        while len(_store) > MAX_SESSIONS:
            _store.popitem(last=False)