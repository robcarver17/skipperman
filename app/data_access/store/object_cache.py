import datetime
import os
import pickle
from typing import Dict, List

from app.data_access.file_access import delete_all_files_in_directory
from app.data_access.store.file_lock import LockFileWithAFile
from app.data_access.store.object_store_elements import CachedDataItem
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

    def get(self, key,  default = NOT_IN_STORE) -> CachedDataItem:
        return self.cache.get(key, default)

    def update(self, new_object: CachedDataItem):
        self.cache[new_object.key] = new_object

    def pop_from_memcache_and_persistent_storage(self, key):
        self.pop_from_memcache(key)
        self.pop_from_persistent(key)

    def pop_from_memcache(self, key):
        self.cache.pop(key)

    def clear_persistent_and_in_memory(self):
        self.clear_in_memory_only()
        self.clear_persistent()

    def clear_in_memory_only(self):
        self._cache = {}

    def keys(self) -> List[CachedDataItem]:
        return list(self.cache.keys())

    def values(self) -> List[CachedDataItem]:
        return list(self.cache.values())

    ## methods need overriding for persistent cache
    def clear_persistent(self):
        pass

    def save_cache(self):
        ## simple does not persist
        pass

    def pop_from_persistent(self, key:str):
        pass

    @property
    def cache(self) -> dict:
        return self._cache

## implements a lockable shared store with a pickler
FILENAME_OF_STORAGE = "storage.pck"
FILENAME_OF_LOCK = "lockfile.pck"
FILENAME_OF_TIMESTAMPS = "timestamps.pck"
ARBITRARY_OLD_DATE=datetime.datetime(1990,1,1)

class PickledObjectCache(SimpleObjectCache):
    def __init__(self, pickle_directory: str):
        self._pickle_directory = pickle_directory

        super().__init__()

    ## LOCKING
    def lock(self):
        self.lock_in_file.lock()

    def force_cache_unlock(self):
        self.lock_in_file.force_cache_unlock()

    def unlock(self):
        self.lock_in_file.unlock()

    @property
    def is_locked_by_another_thread(self):
        return self.lock_in_file.is_locked_by_another_thread

    @property
    def lock_in_file(self) -> LockFileWithAFile:
        lock =  getattr(self, "_lock_file", None)
        if lock is None:
            lock = LockFileWithAFile(self.filename_for_lock)
            self._lock_file = lock

        return lock

    ## CACHE OPERATIONS
    def clear_persistent(self):
        self.force_cache_unlock()
        self.delete_all_cache_files_from_disk()

    def get(self, key, default:  [CachedDataItem, object]= NOT_IN_STORE) -> CachedDataItem:
        underyling_store = self.cache
        if self.key_exists_in_underyling_cache(key):
            if self.data_we_have_for_key_is_fresh(key):
                return underyling_store.get(key)

        return self.get_and_return_object_from_disk_and_refresh_mem_cache(key, default=NOT_IN_STORE)

    def get_and_return_object_from_disk_and_refresh_mem_cache(self, key: str, default: [CachedDataItem, object]=NOT_IN_STORE)-> CachedDataItem:
        if key in self.list_of_keys_to_delete_on_save:
            ## treat as deleted
            return default

        object_from_disk = self.get_cached_on_disk_object_or_default_for_key(key, default=default)
        if object_from_disk is default:
            return default

        timestamp_from_disk = self.timestamp_from_disk_for_cached_item(key)

        self.update_timestamp_held_in_memory(key, new_timestamp=timestamp_from_disk)
        self.update_mem_cache(key=key, new_object=object_from_disk)

        return object_from_disk

    def update(self, new_data_item: CachedDataItem):
        object_exists_already = self.key_exists_in_underyling_cache(new_data_item.key)

        if object_exists_already:
            existing_object = self.cache.get(new_data_item.key)
            if existing_object.contents == new_data_item.contents:
                ## no change
                return

        self.perform_update_of_new_or_modified_object(new_data_item)

    def perform_update_of_new_or_modified_object(self, new_data_item: CachedDataItem):
        new_data_item.changed = True
        self.update_mem_cache(new_data_item.key, new_data_item)
        self.update_timestamp_held_in_memory(new_data_item.key, datetime.datetime.now())

    def update_mem_cache(self, key, new_object):
        self.cache[key] = new_object

    def save_cache(self):

        if self.is_locked_by_another_thread:
            raise CacheIsLocked("Can't save to a locked cache")

        for key in self.cache.keys():
            self.save_cache_for_key_in_memory(key)

        self.bulk_deletion_of_popped_items()

    def save_cache_for_key_in_memory(self, key):
        local_object = self.cache[key]
        if not local_object.changed_vs_persistent:
            return

        local_timestamp =self.timestamps_of_cache_held_in_memory[key]

        self.update_shared_cache_for_key(new_object=local_object, key=key)
        self.update_timestamp_held_on_disk(new_timestamp=local_timestamp, key=key)

    ## PERSTISTENT CACHE OPERATIONS
    def data_we_have_for_key_is_fresh(self, key: str):
        my_timestamps = self.timestamps_of_cache_held_in_memory
        my_timestamp_this_key = my_timestamps.get(key, ARBITRARY_OLD_DATE)
        latest_timestamp_on_disk_this_key = self.timestamp_from_disk_for_cached_item(key, ARBITRARY_OLD_DATE)

        return my_timestamp_this_key>=latest_timestamp_on_disk_this_key

    def data_we_have_for_key_is_newer_than_on_disk(self, key: str):
        my_timestamps = self.timestamps_of_cache_held_in_memory
        my_timestamp_this_key = my_timestamps.get(key, ARBITRARY_OLD_DATE)
        latest_timestamp_on_disk_this_key = self.timestamp_from_disk_for_cached_item(key, ARBITRARY_OLD_DATE)

        return my_timestamp_this_key>latest_timestamp_on_disk_this_key

    def update_timestamp_held_in_memory(self, key, new_timestamp: datetime.datetime):
        timestamps = self.timestamps_of_cache_held_in_memory
        timestamps[key] = new_timestamp
        self.timestamps_of_cache_held_in_memory = timestamps

    def update_timestamp_held_on_disk(self, key, new_timestamp: datetime.datetime):
        timestamps = self.get_dict_of_timestamps_or_default_from_disk(default={})
        timestamps[key] = new_timestamp
        self.update_dict_of_timestamps_on_disk(timestamps)

    @property
    def timestamps_of_cache_held_in_memory(self):
        return getattr(self, "_cache_timestamps", {})

    @timestamps_of_cache_held_in_memory.setter
    def timestamps_of_cache_held_in_memory(self, timestamp_dict: Dict[str, datetime.datetime]):
        setattr(self, "_cache_timestamps", timestamp_dict)

    def timestamp_from_disk_for_cached_item(self, key: str, default = ARBITRARY_OLD_DATE):
        latest_timestamp_on_disk = self.get_dict_of_timestamps_or_default_from_disk(default={})
        return latest_timestamp_on_disk.get(key, default)

    def key_exists_in_underyling_cache(self, key):
        return key in self.cache.keys()

    @property
    def cache(self) -> Dict[str, CachedDataItem]:
        cache = getattr(self, "_cache", None)
        if cache is None:
            return self.setup_and_return_in_memory_cache()

        return cache

    def setup_and_return_in_memory_cache(self) -> dict:
        self._cache = {}
        self.timestamps_of_cache_held_in_memory = {}

        return self._cache

    ## disk operations
    def pop_from_persistent(self, key:str):
        self.add_key_to_delete_on_save(key)

    def bulk_deletion_of_popped_items(self):
        while len(self.list_of_keys_to_delete_on_save)>0:
            key = self.list_of_keys_to_delete_on_save[0]
            filename = self.filename_for_cached_value_of_key(key)
            try:
                os.remove(filename)
            except:
                pass
            self.mark_key_as_deleted(key)

    def delete_all_cache_files_from_disk(self):
        delete_all_files_in_directory(self.pickle_directory)

    def get_cached_on_disk_object_or_default_for_key(self, key: str, default=None):
        fname = self.filename_for_cached_value_of_key(key)
        try:
            with open(fname, "rb") as f:
                return pickle.load(f)
        except:
            return default

    def update_shared_cache_for_key(self, new_object, key: str):
        fname = self.filename_for_cached_value_of_key(key)
        with open(fname, "wb") as f:
            pickle.dump(new_object , f)

    def get_dict_of_timestamps_or_default_from_disk(self, default = None):
        fname = self.filename_for_timestamps
        try:
            with open(fname, "rb") as f:
                return pickle.load(f)
        except:
            return default

    def update_dict_of_timestamps_on_disk(self, new_dict: Dict[str, datetime.datetime]):
        with open(self.filename_for_timestamps, "wb") as f:
            pickle.dump(new_dict , f)

    @property
    def list_of_keys_to_delete_on_save(self):
        return getattr(self, "_keys_to_delete", [])

    def add_key_to_delete_on_save(self, new_key: str):
        original_list = self.list_of_keys_to_delete_on_save
        original_list.append(new_key)
        self._keys_to_delete = original_list

    def mark_key_as_deleted(self, key: str):
        original_list = self.list_of_keys_to_delete_on_save
        try:
            original_list.remove(key)
        except:
            pass

        self._filenames_to_delete = original_list



    def filename_for_cached_value_of_key(self, key:str):
        fname = os.path.join(self.pickle_directory, "stored_value_for_%s.pck" % key)

        return fname

    @property
    def filename_for_lock(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_LOCK)

        return fname


    @property
    def filename_for_timestamps(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_TIMESTAMPS)

        return fname


    @property
    def pickle_directory(self) -> str:
        return self._pickle_directory

