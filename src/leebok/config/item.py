class item(object):
    def __init__(self, fget):
        self._fget = fget
        self._name = fget.__name__
        self._cache = UNCACHED

    def __get__(self, obj, typ):
        if obj is None:
            return self
        if self._cache is UNCACHED:
            self._cache = self._fget(obj)
        return self._cache

    def __set__(self, obj, val):
        setattr(obj, f'_{self._name}', val)


UNCACHED = object()
