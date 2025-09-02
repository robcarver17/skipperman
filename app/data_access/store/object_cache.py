import datetime
import os
import pickle
import random
from typing import Union

from app.objects.utilities.exceptions import CacheIsLocked

NOT_IN_STORE = object()

class SimpleObjectCache():
    def __init__(self):
        self._cache = {}

    ## locking not implemented as not shared
    def lock(self):
        pass

    def unlock(self):
        pass

    def force_cache_unlock(self):
        ## allows anyone to clear the cache lock
        pass

    @property
    def is_locked_by_another_thread(self):
        return False

    def save_cache(self):
        ## simple does not persist
        pass

    def key_exists_in_underyling_cache(self, key):
        return key in self.cache.keys()

    def get(self, key, default = NOT_IN_STORE):
        return self.cache.get(key, default)

    def update(self, key, new_object):
        self.cache[key] = new_object

    def clear_persistent_and_in_memory(self):
        self.clear_in_memory_only()
        self.clear_persistent()

    def clear_in_memory_only(self):
        self._cache = {}


    def clear_persistent(self):
        pass

    @property
    def cache(self) -> dict:
        return self._cache

## implements a lockable shared store with a pickler
FILENAME_OF_STORAGE = "storage.pck"
FILENAME_OF_LOCK = "lockfile.pck"
NOT_LOCKED = -1

class PickledObjectCache(SimpleObjectCache):
    def __init__(self, pickle_directory: str):
        self._pickle_directory = pickle_directory
        super().__init__()

    ## LOCKING
    def lock(self):
        if self.is_locked_by_another_thread:
            raise CacheIsLocked("Can't lock, already locked by someone else")

        if self.is_locked_by_me:
            ## can't lock twice
            return

        assert self.is_unlocked

        self.create_lockfile_and_store_lock()

    def force_cache_unlock(self):
        ## allows anyone to clear the cache lock
        self.remove_lockfile_and_stored_lock()


    def unlock(self):
        if self.is_unlocked:
            ## can't unlock twice
            return

        if self.is_locked_by_another_thread:
            raise CacheIsLocked("Can't unlock, already locked by someone else")

        assert self.is_locked_by_me

        self.remove_lockfile_and_stored_lock()


    @property
    def is_locked_by_another_thread(self):
        if self.is_unlocked:
            return False
        locked_by_me = self.my_lock_id_matches_file_lock

        return not locked_by_me

    @property
    def is_locked_by_me(self):
        if self.is_unlocked:
            return False
        locked_by_me = self.my_lock_id_matches_file_lock
        return locked_by_me

    def create_lockfile_and_store_lock(self):
        id =random.randint(0, 1000000)
        self.create_lock_file_with_id(id)
        self.my_lock_id = id

    def remove_lockfile_and_stored_lock(self):
        self.clear_lock_file()
        self.clear_my_lock_id()

    @property
    def is_locked_by_anyone(self):
        return not self.is_unlocked

    @property
    def is_unlocked(self):
        lock_id = self.read_lock_id_from_file(default = NOT_LOCKED)
        return lock_id is NOT_LOCKED

    @property
    def my_lock_id_matches_file_lock(self):
        file_id = self.read_lock_id_from_file()
        my_id = self.my_lock_id

        return file_id == my_id

    def create_lock_file_with_id(self, new_id: int):
        assert self.is_unlocked
        with open(self.filename_for_lock, "wb") as f:
            pickle.dump(new_id , f)

    def read_lock_id_from_file(self, default=NOT_LOCKED):
        fname = self.filename_for_lock
        if os.path.isfile(fname):
            with open(fname, "rb") as f:
                return pickle.load(f)
        else:
            return default

    def clear_lock_file(self):
        filename = self.filename_for_lock
        try:
            os.remove(filename)
        except:
            pass

    def clear_my_lock_id(self):
        self.my_lock_id = NOT_LOCKED

    @property
    def my_lock_id(self) -> int:
        return getattr(self, "_lock_id", NOT_LOCKED)

    @my_lock_id.setter
    def my_lock_id(self, new_id:int ):
        self._lock_id = new_id

    ## CACHE OPERATIONS
    def clear_in_memory_only(self):
        self._cache = {}

    def clear_persistent(self):
        self.remove_lockfile_and_stored_lock()
        self.create_empty_shared_cache_on_disk_and_return()

    def get(self, key, default = NOT_IN_STORE):
        underyling_store = self.cache

        return underyling_store.get(key, default)


    def update(self, key, new_object):
        object_exists_already = not self.key_exists_in_underyling_cache(key)

        if object_exists_already:
            existing_object = self.cache.get(key)
            if existing_object == new_object:
                ## no change
                return

        self.perform_update_of_new_or_modified_object(key, new_object)


    def save_cache(self):
        no_change = not self.underlying_has_changed
        if no_change:
            return

        if self.is_locked_by_another_thread:
            raise CacheIsLocked("Can't save to a locked cache")

        self.update_shared_cache(self.cache)


    def perform_update_of_new_or_modified_object(self, key, new_object):
        self.flag_change_to_underlying()
        self.cache[key] = new_object

    ## PERSTISTENT CACHE OPERATIONS
    @property
    def underlying_has_changed(self):
        return getattr(self, "_changed", False)

    def flag_change_to_underlying(self):
        self._changed = True

    @property
    def cache(self) -> dict:
        cache = getattr(self, "_cache", None)
        if cache is None:
            return self.setup_and_return_persistent_cache()

        return cache

    def setup_and_return_persistent_cache(self) -> dict:
        shared_cache = self.get_shared_cache_or_default(default=None)

        if (shared_cache is None):
            shared_cache = self.create_empty_shared_cache_on_disk_and_return()

        self._cache = shared_cache
        self._changed = False

        return shared_cache

    def create_empty_shared_cache_on_disk_and_return(self) -> dict:
        shared_cache = {}
        self.update_shared_cache(shared_cache)

        return shared_cache

    def get_shared_cache_or_default(self, default=None):
        fname = self.filename_for_data
        if os.path.isfile(fname):
            with open(fname, "rb") as f:
                return pickle.load(f)
        else:
            return default

    def update_shared_cache(self, new_dict):
        with open(self.filename_for_data, "wb") as f:
            pickle.dump(new_dict , f)



    @property
    def filename_for_lock(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_LOCK)

        return fname

    @property
    def filename_for_data(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_STORAGE)

        return fname



    @property
    def pickle_directory(self) -> str:
        return self._pickle_directory