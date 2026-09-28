import satellite
from satellite import *
import datetime
import os
from glob import glob
from osgeo import gdal

class MSG0DegreeDataSource(satellite.DataSource):
    def __init__(self):
        self.consumer_key = satellite.Config.eumetsat_consumer_key
        self.consumer_secret = satellite.Config.eumetsat_consumer_secret
        self.name = "MSG 0 Degree"
        self.id = "MSG0"

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from EUMETSAT

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        self.recent_file_prefix = file_prefix
        credentials = (self.consumer_key, self.consumer_secret)
        token = eumdac.AccessToken(credentials, cache=False)

        print(f"This token '{token}' expires {token.expiration}")

        collection = 'EO:EUM:DAT:MSG:HRSEVIRI'
        datastore = eumdac.DataStore(token)
        selected_collection = datastore.get_collection(collection)
        print(selected_collection.title)

        # display(selected_collection.search_options)
        end_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        start_time = end_time - datetime.timedelta(hours=24)
        print('Filtering data >1hr based on licensing terms')

        products = selected_collection.search(dtstart=start_time, dtend=end_time)
        product = products.first()
        print(product)

        try:
            with product.open() as fsrc :
                self.recent_path = f'{Config.output_dir}/{file_prefix}_{fsrc.name}'
                with open(self.recent_path, mode='wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
                    print(f'Download of product {product} finished.')
                    
            # extract zip
            print('Extracting . . .')
            subprocess.run(["unzip", self.recent_path, "-d", self.recent_path[:-len('.zip')]])
            self.recent_path = f"{self.recent_path[:-len('.zip')]}/{self.recent_path.split('_')[-1][:-len('zip')]}nat"
            print('Recent file changed to ' + self.recent_path)

        except eumdac.product.ProductError as error:
            print(f"Error related to the product '{product}' while trying to download it: '{error}'")
        except requests.exceptions.ConnectionError as error:
            print(f"Error related to the connection: '{error}'")
        except requests.exceptions.RequestException as error:
            print(f"Unexpected error: {error}")

    def toNetCDF(self, bands=['VIS006', 'VIS008', 'IR_016']):
        '''
        References
        ----------
        https://satpy.readthedocs.io/en/stable/api/satpy.scene.html
        https://satpy.readthedocs.io/en/stable/writing.html
        '''
        name_tags = f"{self.recent_file_prefix}[{self.id}]"
        # read in the .nat
        scn = Scene(
            filenames=[self.recent_path],
            reader='seviri_l1b_native')
        # output to GeoTIFF(s)
        scn.load(
            [band for band in scn.available_dataset_names() if band !='HRV'],
            upper_right_corner='NE'
        )
        print(f'{name_tags} resampling . . . ')
        resampled = scn.resample('msg_seviri_fes_3km')
        print(f'{name_tags} saving . . . ')
        resampled.save_datasets(
            filename=name_tags + "{name}_{start_time:%Y%m%d_%H%M%S}.tif",
            base_dir=Config.output_dir,
            writer="geotiff",
            driver="COG"
        )
        print(f"{name_tags} Transformed {self.recent_path} into GeoTiffs.")
        vrt_path = f'{Config.output_dir}{name_tags}.vrt'
        tif_paths = [path for path in os.listdir(Config.output_dir)
                     if name_tags in path and any(band in path for band in bands)]
        combo_tifs_path = f'{Config.output_dir}{name_tags}_combined.tif'
        netcdf_path = f'{Config.output_dir}{name_tags}.nc'
        print(f"{name_tags} Combining GeoTiffs . . .{'\n\t'.join(tif_paths)}")
        gdal.BuildVRT(vrt_path, tif_paths, separate=True)
        gdal.Translate(
            combo_tifs_path,
            vrt_path,
            format="COG",
            creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'BIGTIFF=IF_SAFER']
        )
        print(f'{name_tags} Done. Creating NetCDF . . .')
        gdal.Warp(
            netcdf_path,
            combo_tifs_path,
            dstSRS="EPSG:4326",
            format="netCDF",
            creationOptions=['COMPRESS=DEFLATE', 'ZLEVEL=9']
        )
        print(f"Transformed {self.recent_path} into a NetCDF.")
        pass
