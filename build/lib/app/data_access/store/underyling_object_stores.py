import datetime
import os
import pickle
from typing import Dict, Union

NOT_IN_STORE = object()

class SimpleUnderlyingStore():
    def __init__(self):
        self._underyling_store = {}

    def save_store(self):
        ## simple does not persist
        pass

    def not_in_underyling_store(self, key):
        in_store = key in self.underyling_store.keys()

        return not in_store

    def get(self, key, default = NOT_IN_STORE):
        return self.underyling_store.get(key, default)

    def update(self, key, new_object):
        self.underyling_store[key] = new_object

    def clear(self):
        self._underyling_store = {}

    @property
    def underyling_store(self) -> dict:
        return self._underyling_store

## implements a shared store with a pickler
FILENAME_OF_STORAGE = "storage.pck"
FILENAME_OF_DATE_KEY = "datekey.pck"

### FIXME: NEED TO AVOID THIS AT SOME POINTS, EG FOR INSTRUCTORS

class PickledSharedStore(SimpleUnderlyingStore):
    def __init__(self, pickle_directory: str):
        self._pickle_directory = pickle_directory
        super().__init__()

    def get(self, key, default = NOT_IN_STORE):
        if self.shared_store_has_changed_since_last_loaded():
            ## DO WE REALLY WANT TO DO THIS? WILL LEAD TO WEIRD EDGE CASES???
            underyling_store = self.setup_and_return_shared_store()
        else:
            underyling_store = self.underyling_store

        return underyling_store.get(key, default)

    def update(self, key, new_object):
        if self.not_in_underyling_store(key):
            pass
        else:
            existing_object = self.underyling_store.get(key)
            if existing_object == new_object:
                return

        self.perform_update_of_new_or_modified_object(key, new_object)

    def perform_update_of_new_or_modified_object(self, key, new_object):
        self.flag_change_to_underlying()
        self.underyling_store[key] = new_object

    @property
    def underlying_has_changed(self):
        return getattr(self, "_changed", False)

    def flag_change_to_underlying(self):
        self._changed = True

    @property
    def underyling_store(self) -> dict:
        store = getattr(self, "_underyling_store", None)
        if store is None:
            return self.setup_and_return_shared_store()
        else:
            ## THINK CAREFULLY ABOUT EDGE CASES
            if self.shared_store_has_changed_since_last_loaded():
                return self.setup_and_return_shared_store()

        return store

    def setup_and_return_shared_store(self) -> dict:
        shared_store = self.get_shared_storage_or_default(NOT_IN_STORE)
        shared_store_timestamp = self.get_timestamp_of_shared_store_from_file(NOT_IN_STORE)

        if (shared_store is NOT_IN_STORE) or (shared_store_timestamp is NOT_IN_STORE):
            shared_store = {}
            self.update_shared_store(shared_store)
            shared_store_timestamp = datetime.datetime.now()
            self.update_shared_store_timestamp_file(shared_store_timestamp)

        self._underyling_store = shared_store
        self._timestamp_shared = shared_store_timestamp
        self._changed = False

        return shared_store


    def saved_timestamp_of_shared_store_or_none(self) -> datetime.datetime:
        return getattr(self, "_timestamp_shared", None)

    def save_store(self):
        if self.underlying_has_changed:
            if self.shared_store_has_changed_since_last_loaded():
                pass
            else:
                self.update_shared_store(self.underyling_store)

    def shared_store_has_changed_since_last_loaded(self):
        timestamp_from_file = self.get_timestamp_of_shared_store_from_file()
        current_timestamp = self.saved_timestamp_of_shared_store_or_none(key)

        if timestamp_from_file is NOT_IN_STORE:
            return False ## no shared store to change
        elif current_timestamp is None:
            return False
        else:
            return timestamp_from_file>current_timestamp

    def get_shared_storage_or_default(self,default=NOT_IN_STORE):
        fname = self.filename_for_data
        if os.path.isfile(fname):
            with open(fname, "rb") as f:
                return pickle.load(f)
        else:
            return default

    def update_shared_store(self, new_dict):
        with open(self.filename_for_data, "wb") as f:
            pickle.dump(new_dict , f)

    def get_timestamp_of_shared_store_from_file(self, default=NOT_IN_STORE) -> Union[datetime.datetime, object]:
        fname = self.filename_for_datekey
        if os.path.isfile(fname):
            with open(fname, "rb") as f:
                return pickle.load(f)
        else:
            return default

    def update_shared_store_timestamp_file(self, new_timestamp: datetime.datetime):
        with open(self.filename_for_datekey, "wb") as f:
            pickle.dump(new_timestamp , f)

    def clear_shared_storage(self):
        os.rmdir(self.pickle_directory)

    @property
    def filename_for_data(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_STORAGE)

        return fname

    @property
    def filename_for_datekey(self):
        fname = os.path.join(self.pickle_directory, FILENAME_OF_DATE_KEY)

        return fname

    @property
    def pickle_directory(self) -> str:
        return self._pickle_directory