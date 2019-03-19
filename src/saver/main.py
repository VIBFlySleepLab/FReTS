import logging, coloredlogs
import pandas as pd
import os.path
import datetime
coloredlogs.install()



# https://stackoverflow.com/questions/16740887/how-to-handle-incoming-real-time-data-with-python-pandas/17056022
CACHE = {}
STORE = 'store'   # Note: another option is to keep the actual file open
max_len = 5000


class Saver():

    def __init__(self, store=STORE, cache = CACHE, datetime = True):
        self.store = store 
        self.cache = cache
        self.log = logging.getLogger(__name__)
        i = 0
        # https://stackoverflow.com/questions/17383716/python-accessing-attributes-and-methods-of-one-class-in-another
        self.parent = None

        #while os.path.isfile(self.store + ".h5") or os.path.isfile(self.store + ".csv"):
        #    i += 1
        #    self.store = "{}_{}".format(store, i)


    def update_parent(self, parent):
        self.parent = parent
        self.store = "{}__{}".format(self.store, self.parent.start_time.strftime("%H%M%S-%d%m%Y"))


    def process_row(self, d, key, max_len = 5000):
        """
        Append row d to the store 'key'.
    
        When the number of items in the key's cache reaches max_len,
        append the list of rows to the HDF5 store and clear the list.
    
        """
        # keep the rows for each key separate.
        lst = self.cache.setdefault(key, [])
        if len(lst) >= max_len:
            self.store_and_clear(lst, key)
        lst.append(d)
        self.log.debug("Adding new datapoint to cache")
    
    def store_and_clear(self, lst, key):
        """
        Convert key's cache list to a DataFrame and append that to HDF5.
        """
        self.log.info("Cleaning cache")
        df = pd.DataFrame(lst)

        # try saving to hdf5
        try:
            with pd.HDFStore(self.store + ".h5") as store:
                store.append(key, df)
        except Exception as e:
            self.log.error("Could not save cache to h5 file. Please investigate traceback")
            self.log.exception(e)
        # save to csv
        with open(self.store + ".csv", 'a') as store:
            df.to_csv(store)

        lst.clear()
