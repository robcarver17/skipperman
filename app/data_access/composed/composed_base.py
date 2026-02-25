
class ComposedBaseData(object):
    def __init__(self, object_store: 'ObjectStore'):
        self._object_store = object_store

    @property
    def object_store(self):
        return self._object_store
