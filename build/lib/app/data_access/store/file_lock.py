import os
import pickle
from random import randint

from app.objects.utilities.exceptions import CacheIsLocked

NOT_LOCKED = -1


class LockFileWithAFile():
    def __init__(self, lock_file_path_and_name:str):
        self.filename_for_lock = lock_file_path_and_name

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
        id =randint(0, 1000000) ## sufficiently large to make collisions unlikely
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
        try:
            with open(fname, "rb") as f:
                return pickle.load(f)
        except:
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
