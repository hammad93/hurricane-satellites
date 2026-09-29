import os
import eumdac
import datetime
import xmltodict
import hashlib
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

class Config(ABC):
    GOES_EAST_STATIC_URL = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/GOES16-ABI-FD-GEOCOLOR-10848x10848.tif"
    GOES_WEST_STATIC_URL = "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/FD/GEOCOLOR/GOES18-ABI-FD-GEOCOLOR-10848x10848.tif"
    h8_link = "https://himawari8.nict.go.jp/img/FULL_24h/latest.json?_={time}"
    eumetsat_consumer_key = os.getenv('EUMETSAT_PASS')
    eumetsat_consumer_secret = os.getenv('EUMETSAT_SECRET')
    output_base = os.getenv('OUTPUT_DIR', './content')
    timestamp = int(datetime.datetime.utcnow().timestamp())
    output_dir_name = f"hurricane-satellites-{timestamp}"
    output_dir = os.path.join(output_base, output_dir_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

class DataSource(ABC):
    
    def __init__(self):
        self.id = None

    @abstractmethod
    def getRecentData(self):
        """Fetch the most recent data from the source."""
        pass

    @abstractmethod
    def toNetCDF(self):
        """
        Convert the data into NetCDF format.
        """
        pass

    def createLayer(self, bands=None):
        '''
        Creates a layer (assumes one doesn't exist). Required only for WMS
        :return:
        '''
        # TODO
        if bands is None:
            bands = ['Band1', 'Band2', 'Band3']
        work_dir = f'{Config.output_base}/workspaces/{os.environ.get("GEOSERVER_WORKSPACE")}'
        store_dir = f'{work_dir}/{self.id}'
        store_url = f"file:{Config.output_dir_name}/{os.path.basename(self.recent_netcdf_path)}"
        # get workspace id
        with open(f'{work_dir}/workspace.xml') as f:
            work_data = xmltodict.parse(f.read())
            work_id = work_data['workspace']['id']
        # get style id
        with open(f'{Config.output_base}/styles/raster.xml') as f:
            style_data = xmltodict.parse(f.read())
            style_id = style_data['style']['id']
        # get namespace id
        with open(f'{work_dir}/namespace.xml') as f:
            namespace_data = xmltodict.parse(f.read())
            self.namespace_id = namespace_data['namespace']['id']
        coverage_ts = f'{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}.00 UTC'
        self.coverage_id = hashlib.md5(self.id.encode('utf')).hexdigest()[:11]
        self.coveragestore_id = f'CoverageStoreInfoImpl-45f169cd:{self.coverage_id}:-7976'
        coveragestore = f'''<coverageStore>
          <id>{self.coveragestore_id}</id>
          <name>{self.id}</name>
          <type>NetCDF</type>
          <enabled>true</enabled>
          <workspace>
            <id>{work_id}</id>
          </workspace>
          <__default>false</__default>
          <dateCreated>{coverage_ts}</dateCreated>
          <disableOnConnFailure>false</disableOnConnFailure>
          <url>{store_url}</url>
        </coverageStore>'''
        # create directory
        os.makedirs(store_dir, exist_ok=True)
        # create coverage store
        with open(f'{store_dir}/coveragestore.xml', 'w') as f:
            f.write(coveragestore)
        # create layer
        os.makedirs(f'{store_dir}/{self.id}', exist_ok=True)
        layer = f'''<layer>
          <name>GOES-16</name>
          <id>LayerInfoImpl-45f169cd:{self.coverage_id}:-7979</id>
          <type>RASTER</type>
          <defaultStyle>
            <id>{style_id}</id>
          </defaultStyle>
          <resource class="coverage">
            <id>{self.coveragestore_id}</id>
          </resource>
          <attribution>
            <logoWidth>0</logoWidth>
            <logoHeight>0</logoHeight>
          </attribution>
          <dateCreated>{coverage_ts}</dateCreated>
        </layer>'''
        with open(f'{work_dir}/{self.id}/{self.id}/layer.xml', 'w') as f:
            f.write(layer)
        # finalize
        layer_coverage = self.generate_coverage()
        with open(f'{work_dir}/{self.id}/{self.id}/coverage.xml', 'w') as f:
            f.write(layer_coverage)
        print(f"Completed create layer for {self.id}")

    def generate_coverage(self):
        raise NotImplementedError
