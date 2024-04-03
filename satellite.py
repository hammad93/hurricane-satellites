import os
import eumdac
import datetime
import shutil
import requests
import dateutil
import subprocess
import satpy
from satpy import Scene
from glob import glob
from osgeo import gdal
from PIL import Image
from urllib.request import urlretrieve
from concurrent.futures import ThreadPoolExecutor, as_completed

from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def getRecentData(self):
        """Fetch the most recent data from the source."""
        pass

    @abstractmethod
    def toNetCDF(self, existing_netcdf_path=None):
        """
        Convert the data into NetCDF format.

        Parameters:
        - existing_netcdf_path (str): Path to an existing NetCDF file to which the new data will be added. If None, create a new NetCDF file.
        """
        pass

