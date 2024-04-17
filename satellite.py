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

class Config:
    GOES_EAST_STATIC_URL = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/GOES16-ABI-FD-GEOCOLOR-10848x10848.tif"
    GOES_WEST_STATIC_URL = "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/FD/GEOCOLOR/GOES18-ABI-FD-GEOCOLOR-10848x10848.tif"
    h8_link = "https://himawari8.nict.go.jp/img/FULL_24h/latest.json?_={time}"
    eumetsat_consumer_key = os.getenv('eumetsat_pass')
    eumetsat_consumer_secret = os.getenv('eumetsat_secret')
    output_dir = '/content'

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

