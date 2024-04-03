class Himawari8DataSource(DataSource):
    def __init__(self):
        self.link = Config.h8_link
        self.name = "Himawari 8"
        self.id = "H8"

    def jpn_get_latest_metadata(self):
      time = int(datetime.datetime.now().timestamp() * 1000)
      return requests.get(self.link).json()

    def jpn_create_urls(self, band):
      dimension = 10
      metadata = self.jpn_get_latest_metadata()
      parsed_time = dateutil.parser.parse(metadata['date'])
      template_url = f"https://himawari8.nict.go.jp/img/FULL_24h/B{band:02}/10d/550/{parsed_time.year}/{parsed_time.strftime('%m')}/{parsed_time.day}/{parsed_time.strftime('%H%M%S')}" #_3_3.png
      result_urls = []
      for i in range(dimension) :
        for j in range(dimension) :
          result_urls.append(template_url + f"_{i}_{j}.png")
      return result_urls

    def download_image(self, file_prefix, band_index, url):
        """
        Download a single image and save it.
        """
        try:
            filename = f"{file_prefix}_{band_index}_{url.split('/')[-1]}"
            print(f"Himarwari 8 downloading {filename}")
            save_path = os.path.join(Config.output_dir, filename)
            urlretrieve(url, save_path)
            return save_path
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return None

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from Himawari 8 and save it with an optional prefix.
        """
        download_paths = []  # To store paths of successfully downloaded files
        with ThreadPoolExecutor() as executor:
            # Create a list to hold futures
            futures = []
            for band_index in [1, 2, 3]:
                for url in self.jpn_create_urls(band_index):
                    # Schedule the download_image method to be executed and store the future
                    futures.append(executor.submit(self.download_image, file_prefix, band_index, url))

            # as_completed will yield futures as they complete
            for future in as_completed(futures):
                path = future.result()  # Get the result from the future
                if path:
                    download_paths.append(path)

        if download_paths:
            print(f"Files saved: {download_paths}")
            self.file_prefix = f"{file_prefix}[{self.id}]"
            self.download_paths = download_paths
            return download_paths  # Return the paths of the saved files for further processing
        else:
            print("Failed to download any files.")
            return None

    def toNetCDF(self, existing_netcdf_path=None):
        '''
        https://gis.stackexchange.com/questions/188500/georeferencing-himawari-8-in-gdal-or-other
        '''
        # Define the size of each tile and the number of tiles in each dimension
        tile_size = 550
        grid_size = 10

        # Function to parse coordinates from filename
        def get_coordinates(filename):
            parts = filename.split('_')
            x = int(parts[-2])
            y = int(parts[-1].split('.')[0])
            return x, y

        # Function to get the imagery band (e.g. VIS, IR)
        def get_band(filename):
            parts = filename.split('_')
            band = int(parts[-4])
            return band

        # Loop through the downloaded images and place them in the correct position
        # Satellite band images are combined together
        band_paths = {}
        for filename in self.download_paths:
            band = get_band(filename)
            if band in band_paths.keys():
                band_paths[band].append(filename)
            else:
                band_paths[band] = []

        for band in band_paths.keys() :
          # Create a blank image for the final combined image
          combined_image = Image.new('LA', (tile_size * grid_size, tile_size * grid_size))
          for filename in band_paths[band]:
              if filename.endswith(".png"):
                  x, y = get_coordinates(filename)
                  img = Image.open(filename)

                  # Ensure the image is in grayscale mode 'LA'
                  print(filename)
                  combined_image.paste(img, (x * tile_size, y * tile_size))
              else:
                  print(f"{filename} is not a PNG")

          # Save the combined image
          combined_path = f"{self.file_prefix}_{band}_combined_image_greyscale.png"
          combined_image.save(combined_path)

          #gdal_translate -a_srs "+proj=geos +h=35785863 +a=6378137.0 +b=6356752.3 +lon_0=140.7 +no_defs" -a_ullr -5500000 5500000 5500000 -5500000 PI_H08_20150125_0230_TRC_FLDK_R10_PGPFD.png temp.tif
          recent_GeoTiff = combined_path[:-len('.png')]+'.tif'
          gdal.Translate(outputSRS="+proj=geos +h=35785863 +a=6378137.0 +b=6356752.3 +lon_0=140.7 +no_defs",
                        outputBounds=[-5500000, 5500000, 5500000, -5500000],
                        srcDS=combined_path,
                        destName=recent_GeoTiff)
          #gdalwarp -overwrite -t_srs "+proj=latlong +ellps=WGS84 +pm=140.7" -wo SOURCE_EXTRA=100 temp.tif Himawari8.tif
          gdal.Warp(destNameOrDestDS=combined_path[:-len('.png')]+'[preprocessed].tif',
                    srcDSOrSrcDSTab=recent_GeoTiff,
                    dstSRS="+proj=latlong +ellps=WGS84 +pm=140.7",
                    warpOptions={'SOURCE_EXTRA': 100})

          preprocessed = combined_path[:-len('.png')]+'[preprocessed].tif'
          print(f"Combined image at {combined_path} and preprocessed at {preprocessed}")
          nc_path = combined_path[:-len('tif')] + 'nc'
          ds = gdal.Translate(nc_path, preprocessed, format='NetCDF')
          print(f"Translated to {nc_path}")

