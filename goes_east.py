import satellite
from satellite import *

class GOESEastDataSource(satellite.DataSource):
    def __init__(self):
        self.name = "GOES 16 East"
        self.id = "GOES-16"
        self.data_url = satellite.Config.GOES_EAST_STATIC_URL

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from GOES East and save it with an optional prefix.

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        filename = f"{file_prefix}[{self.id}]_{os.path.basename(self.data_url)}"
        save_path = os.path.join(Config.output_dir, filename)
        self.recent_path = save_path

        try:
            urlretrieve(self.data_url, save_path)
            print(f"File saved as {save_path}")
            self.recent_path = save_path
            return save_path  # Return the path of the saved file for further processing
        except Exception as e:
            print(f"Failed to download the file: {e}")
            return None

    def toNetCDF(self, existing_netcdf_path=None):
        self.recent_netcdf_path = self.recent_path[:-len("tif")] + "nc"
        ds = gdal.Translate(self.recent_netcdf_path, self.recent_path, format='NetCDF')
        print(f"Transformed {self.recent_path} to {self.recent_netcdf_path}")