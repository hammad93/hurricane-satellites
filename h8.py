import satellite
from satellite import *

class Himawari8DataSource(satellite.DataSource):
    def __init__(self):
        self.link = satellite.Config.h8_link
        self.name = "Himawari 8"
        self.id = "H8"

    def jpn_get_latest_metadata(self):
      time = int(datetime.datetime.now().timestamp() * 1000)
      return requests.get(self.link).json()

    def jpn_create_urls(self, band):
      dimension = 10
      metadata = self.jpn_get_latest_metadata()
      parsed_time = dateutil.parser.parse(metadata['date'])
      template_url = f"https://himawari8.nict.go.jp/img/FULL_24h/B{band:02}/10d/550/{parsed_time.year}/{parsed_time.strftime('%m')}/{parsed_time.strftime('%d')}/{parsed_time.strftime('%H%M%S')}" #_3_3.png
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
            filename = f"{file_prefix}[{self.id}]band_{band_index}_{url.split('/')[-1]}"
            print(f"Himarwari 8 downloading {filename}")
            save_path = os.path.join(Config.output_dir, filename)
            urlretrieve(url, save_path)
            return save_path
        except Exception as e:
            print(f"Failed to download {filename} URL {url}: {e}")
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

    def toNetCDF(self):
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

        tif_paths = [] # save the output GeoTiff paths
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
            combined_path = f"{Config.output_dir}/{self.file_prefix}_{band}_combined_image_greyscale.png"
            combined_image.save(combined_path)

            #gdal_translate -a_srs "+proj=geos +h=35785863 +a=6378137.0 +b=6356752.3 +lon_0=140.7 +no_defs" -a_ullr -5500000 5500000 5500000 -5500000 PI_H08_20150125_0230_TRC_FLDK_R10_PGPFD.png temp.tif
            recent_GeoTiff = combined_path[:-len('.png')]+'.tif'
            gdal.Translate(outputSRS="+proj=geos +h=35785863 +a=6378137.0 +b=6356752.3 +lon_0=140.7 +sweep=y +no_defs",
                        outputBounds=[-5500000, 5500000, 5500000, -5500000],
                        srcDS=combined_path,
                        destName=recent_GeoTiff)
            #gdalwarp -overwrite -t_srs "+proj=latlong +ellps=WGS84 +pm=140.7" -wo SOURCE_EXTRA=100 temp.tif Himawari8.tif
            gdal.Warp(destNameOrDestDS=combined_path[:-len('.png')]+'[preprocessed].tif',
                    srcDSOrSrcDSTab=recent_GeoTiff,
                    dstSRS="+proj=latlong +ellps=WGS84 +no_defs",
                    warpOptions={'SOURCE_EXTRA': 100})
            tif_paths.append(recent_GeoTiff)

        # convert to NetCDF
        h8_srs = '+proj=geos +lon_0=140.7 +h=35785863 +x_0=0 +y_0=0 +a=6378137 +rf=298.257024882273 +units=m +no_defs'
        path_prefix = f'{Config.output_dir}/{self.file_prefix}'
        vrt_path = f'{path_prefix}.vrt'
        combo_tifs_path = f'{path_prefix}_all_bands.tif'
        netcdf_path = f'{path_prefix}.nc'
        print(f'{self.file_prefix} Combining GeoTiffs . . .')
        # order the bands in reverse through order of input tifs
        gdal.BuildVRT(vrt_path, tif_paths[::-1], separate=True, bandList=[2])
        gdal.Translate(
            combo_tifs_path,
            vrt_path,
            format="COG",
            outputSRS=h8_srs,
            creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'BIGTIFF=IF_SAFER']
        )
        print(f'{self.file_prefix} Done. Creating NetCDF . . .')
        gdal.Warp(
            netcdf_path,
            combo_tifs_path,
            srcSRS=h8_srs,
            dstSRS="EPSG:4326",
            format="netCDF",
            creationOptions=['COMPRESS=DEFLATE', 'ZLEVEL=9']
        )
        self.recent_netcdf_path = netcdf_path
        print(f'{self.file_prefix} Done. Output to {self.recent_netcdf_path}')

    def generate_coverage(self):
        coverage = f'''<coverage>
          <id>{self.coveragestore_id}</id>
          <name>H8</name>
          <nativeName>H8</nativeName>
          <namespace>
            <id>{self.namespace_id}</id>
          </namespace>
          <title>H8</title>
          <description>Generated from NetCDF</description>
          <keywords>
            <string>H8</string>
            <string>WCS</string>
            <string>NetCDF</string>
          </keywords>
          <nativeCRS>GEOGCS[&quot;WGS 84&quot;, 
          DATUM[&quot;World Geodetic System 1984&quot;, 
            SPHEROID[&quot;WGS 84&quot;, 6378137.0, 298.257223563, AUTHORITY[&quot;EPSG&quot;,&quot;7030&quot;]], 
            AUTHORITY[&quot;EPSG&quot;,&quot;6326&quot;]], 
          PRIMEM[&quot;Greenwich&quot;, 0.0, AUTHORITY[&quot;EPSG&quot;,&quot;8901&quot;]], 
          UNIT[&quot;degree&quot;, 0.017453292519943295], 
          AXIS[&quot;Geodetic longitude&quot;, EAST], 
          AXIS[&quot;Geodetic latitude&quot;, NORTH], 
          AUTHORITY[&quot;EPSG&quot;,&quot;4326&quot;]]</nativeCRS>
          <srs>EPSG:4326</srs>
          <nativeBoundingBox>
            <minx>-179.99999933331813</minx>
            <maxx>179.97761588345176</maxx>
            <miny>-79.70634295228002</miny>
            <maxy>79.68194590002715</maxy>
            <crs>EPSG:4326</crs>
          </nativeBoundingBox>
          <latLonBoundingBox>
            <minx>-179.99999933331813</minx>
            <maxx>179.97761588345176</maxx>
            <miny>-79.70634295228002</miny>
            <maxy>79.68194590002715</maxy>
            <crs>EPSG:4326</crs>
          </latLonBoundingBox>
          <projectionPolicy>REPROJECT_TO_DECLARED</projectionPolicy>
          <enabled>true</enabled>
          <metadata>
            <entry key="COVERAGE_VIEW">
              <coverageView>
                <coverageBands>
                  <coverageBand>
                    <inputCoverageBands class="singleton-list">
                      <inputCoverageBand>
                        <coverageName>Band1</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band1</definition>
                    <index>0</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                  <coverageBand>
                    <inputCoverageBands class="singleton-list">
                      <inputCoverageBand>
                        <coverageName>Band2</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band2</definition>
                    <index>1</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                  <coverageBand>
                    <inputCoverageBands class="singleton-list">
                      <inputCoverageBand>
                        <coverageName>Band3</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band3</definition>
                    <index>2</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                </coverageBands>
                <name>H8</name>
                <envelopeCompositionType>INTERSECTION</envelopeCompositionType>
                <selectedResolution>BEST</selectedResolution>
                <compositionType>BAND_SELECT</compositionType>
                <selectedResolutionIndex>-1</selectedResolutionIndex>
                <outputName></outputName>
                <definition></definition>
                <fillMissingBands>false</fillMissingBands>
              </coverageView>
            </entry>
            <entry key="NetCDFOutput.Key">
              <netcdfLayerSettingsContainer>
                <compressionLevel>0</compressionLevel>
                <shuffle>true</shuffle>
                <copyAttributes>false</copyAttributes>
                <copyGlobalAttributes>false</copyGlobalAttributes>
                <dataPacking>NONE</dataPacking>
              </netcdfLayerSettingsContainer>
            </entry>
            <entry key="dirName">H8_H8</entry>
          </metadata>
          <store class="coverageStore">
            <id>{self.coveragestore_id}</id>
          </store>
          <serviceConfiguration>false</serviceConfiguration>
          <simpleConversionEnabled>false</simpleConversionEnabled>
          <internationalTitle/>
          <internationalAbstract/>
          <nativeFormat>NetCDF</nativeFormat>
          <grid dimension="2">
            <range>
              <low>0 0</low>
              <high>7112 3149</high>
            </range>
            <transform>
              <scaleX>0.05061552519920837</scaleX>
              <scaleY>-0.050615525199208374</scaleY>
              <shearX>0.0</shearX>
              <shearY>0.0</shearY>
              <translateX>-179.97469157071853</translateX>
              <translateY>79.65663813742754</translateY>
            </transform>
            <crs>EPSG:4326</crs>
          </grid>
          <supportedFormats>
            <string>ImageMosaic</string>
            <string>GEOTIFF</string>
            <string>NetCDF</string>
            <string>ArcGrid</string>
            <string>GeoPackage (mosaic)</string>
            <string>GIF</string>
            <string>PNG</string>
            <string>JPEG</string>
            <string>TIFF</string>
          </supportedFormats>
          <interpolationMethods>
            <string>nearest neighbor</string>
            <string>bilinear</string>
            <string>bicubic</string>
          </interpolationMethods>
          <defaultInterpolationMethod>nearest neighbor</defaultInterpolationMethod>
          <dimensions>
            <coverageDimension>
              <name>Band1</name>
              <description>GridSampleDimension[0.0,255.0]</description>
              <range>
                <min>0.0</min>
                <max>255.0</max>
              </range>
              <dimensionType>
                <name>UNSIGNED_8BITS</name>
              </dimensionType>
            </coverageDimension>
            <coverageDimension>
              <name>Band2</name>
              <description>GridSampleDimension[0.0,255.0]</description>
              <range>
                <min>0.0</min>
                <max>255.0</max>
              </range>
              <dimensionType>
                <name>UNSIGNED_8BITS</name>
              </dimensionType>
            </coverageDimension>
            <coverageDimension>
              <name>Band3</name>
              <description>GridSampleDimension[0.0,255.0]</description>
              <range>
                <min>0.0</min>
                <max>255.0</max>
              </range>
              <dimensionType>
                <name>UNSIGNED_8BITS</name>
              </dimensionType>
            </coverageDimension>
          </dimensions>
          <requestSRS>
            <string>EPSG:4326</string>
          </requestSRS>
          <responseSRS>
            <string>EPSG:4326</string>
          </responseSRS>
          <parameters>
            <entry>
              <string>Bands</string>
              <null/>
            </entry>
            <entry>
              <string>Filter</string>
              <null/>
            </entry>
          </parameters>
          <nativeCoverageName>H8</nativeCoverageName>
        </coverage>
        '''
        return coverage
