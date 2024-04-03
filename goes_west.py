class GOESWestDataSource(DataSource):
    def __init__(self):
        self.name = "GOES 18 West"
        self.id = "GOES-18"
        # Updated to point to the GOES-18 GEOCOLOR image
        self.data_url = Config.GOES_WEST_STATIC_URL

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from GOES West (GOES-18) and save it with an optional prefix.

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        filename = f"{file_prefix}_{os.path.basename(self.data_url)}"
        save_path = os.path.join(Config.output_dir, filename)

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
