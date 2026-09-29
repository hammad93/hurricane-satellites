import satellite
from satellite import *
import datetime
from msg_0 import MSG0DegreeDataSource


class MSGIndianOceanDataSource(MSG0DegreeDataSource):
    def __init__(self):
        self.consumer_key = satellite.Config.eumetsat_consumer_key
        self.consumer_secret = satellite.Config.eumetsat_consumer_secret
        self.name = "MSG Indian Ocean"
        self.id = "MSGIO"

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from EUMETSAT

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        self.recent_file_prefix = file_prefix
        credentials = (self.consumer_key, self.consumer_secret)
        token = eumdac.AccessToken(credentials, cache=False)

        print(f"This token '{token}' expires {token.expiration}")

        collection = 'EO:EUM:DAT:MSG:HRSEVIRI-IODC'
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

    def toNetCDF(self):
        return super().toNetCDF()
    def generate_coverage(self):
        coverage = f'''<coverage>
          <id>{self.coveragestore_id}</id>
          <name>MSGIO</name>
          <nativeName>MSGIO</nativeName>
          <namespace>
            <id>{self.namespace_id}</id>
          </namespace>
          <title>MSGIO</title>
          <description>Generated from NetCDF</description>
          <keywords>
            <string>MSGIO</string>
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
            <minx>-81.27513348826551</minx>
            <maxx>81.28857132055</maxx>
            <miny>-74.05266272757707</miny>
            <maxy>74.17827924426628</maxy>
            <crs>EPSG:4326</crs>
          </nativeBoundingBox>
          <latLonBoundingBox>
            <minx>-81.27513348826551</minx>
            <maxx>81.28857132055</maxx>
            <miny>-74.05266272757707</miny>
            <maxy>74.17827924426628</maxy>
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
                        <coverageName>Band10</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band10</definition>
                    <index>0</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                  <coverageBand>
                    <inputCoverageBands class="singleton-list">
                      <inputCoverageBand>
                        <coverageName>Band8</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band8</definition>
                    <index>1</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                  <coverageBand>
                    <inputCoverageBands class="singleton-list">
                      <inputCoverageBand>
                        <coverageName>Band9</coverageName>
                      </inputCoverageBand>
                    </inputCoverageBands>
                    <definition>Band9</definition>
                    <index>2</index>
                    <compositionType>BAND_SELECT</compositionType>
                  </coverageBand>
                </coverageBands>
                <name>MSGIO</name>
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
            <entry key="dirName">MSGIO_MSGIO</entry>
          </metadata>
          <store class="coverageStore">
            <id>{self.coveragestore_id.split(':')[0]}:-7785</id>
          </store>
          <serviceConfiguration>false</serviceConfiguration>
          <simpleConversionEnabled>false</simpleConversionEnabled>
          <internationalTitle/>
          <internationalAbstract/>
          <nativeFormat>NetCDF</nativeFormat>
          <grid dimension="2">
            <range>
              <low>0 0</low>
              <high>3879 3537</high>
            </range>
            <transform>
              <scaleX>0.04190866326600039</scaleX>
              <scaleY>-0.04190866326600038</scaleY>
              <shearX>0.0</shearX>
              <shearY>0.0</shearY>
              <translateX>-81.2541791566325</translateX>
              <translateY>74.15732491263327</translateY>
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
              <name>Band10</name>
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
              <name>Band8</name>
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
              <name>Band9</name>
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
          <nativeCoverageName>MSGIO</nativeCoverageName>
        </coverage>
        '''
        return coverage