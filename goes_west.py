import satellite
from satellite import *

class GOESWestDataSource(satellite.DataSource):
    def __init__(self):
        self.name = "GOES 18 West"
        self.id = "GOES-18"
        # Updated to point to the GOES-18 GEOCOLOR image
        self.data_url = satellite.Config.GOES_WEST_STATIC_URL

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from GOES West (GOES-18) and save it with an optional prefix.

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        filename = f"{file_prefix}[{self.id}]_{os.path.basename(self.data_url)}"
        save_path = os.path.join(satellite.Config.output_dir, filename)

        try:
            urlretrieve(self.data_url, save_path)
            print(f"File saved as {save_path}")
            self.recent_path = save_path
            return save_path  # Return the path of the saved file for further processing
        except Exception as e:
            print(f"Failed to download the file: {e}")
            return None

    def toNetCDF(self):
        self.recent_netcdf_path = self.recent_path[:-len(".tif")] + ".nc"
        ds = gdal.Translate(self.recent_netcdf_path, self.recent_path, format='NetCDF')
        print(f"Transformed {self.recent_path} to {self.recent_netcdf_path}")

    def generate_coverage(self):
        '''
        The XML string for the coverage
        :return: string
        '''
        coverage = f'''<coverage>
          <id>{self.coveragestore_id}</id>
          <name>GOES-18</name>
          <nativeName>GOES-18</nativeName>
          <namespace>
            <id>NamespaceInfoImpl--7f5864fa:{self.coverage_id}:-7ff5</id>
          </namespace>
          <title>GOES-18</title>
          <description>Generated from NetCDF</description>
          <keywords>
            <string>GOES-18</string>
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
            <minx>146.54150390625</minx>
            <maxx>299.49050390624996</maxx>
            <miny>-76.49019873046873</miny>
            <maxy>76.45880126953125</maxy>
            <crs>EPSG:4326</crs>
          </nativeBoundingBox>
          <latLonBoundingBox>
            <minx>146.54150390625</minx>
            <maxx>299.49050390624996</maxx>
            <miny>-76.49019873046873</miny>
            <maxy>76.45880126953125</maxy>
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
                <name>GOES-18</name>
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
            <entry key="dirName">GOES-18_GOES-18</entry>
          </metadata>
          <store class="coverageStore">
            <id>{self.coveragestore_id.split(':')[0]}:-7976</id>
          </store>
          <serviceConfiguration>false</serviceConfiguration>
          <simpleConversionEnabled>false</simpleConversionEnabled>
          <internationalTitle/>
          <internationalAbstract/>
          <nativeFormat>NetCDF</nativeFormat>
          <grid dimension="2">
            <range>
              <low>0 0</low>
              <high>17000 17000</high>
            </range>
            <transform>
              <scaleX>0.008997</scaleX>
              <scaleY>-0.008997</scaleY>
              <shearX>0.0</shearX>
              <shearY>0.0</shearY>
              <translateX>146.54600240625</translateX>
              <translateY>76.45430276953125</translateY>
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
              <description>GridSampleDimension[1.0,255.0]</description>
              <range>
                <min>1.0</min>
                <max>255.0</max>
              </range>
              <nullValues>
                <double>0.0</double>
              </nullValues>
              <dimensionType>
                <name>UNSIGNED_8BITS</name>
              </dimensionType>
            </coverageDimension>
            <coverageDimension>
              <name>Band2</name>
              <description>GridSampleDimension[1.0,255.0]</description>
              <range>
                <min>1.0</min>
                <max>255.0</max>
              </range>
              <nullValues>
                <double>0.0</double>
              </nullValues>
              <dimensionType>
                <name>UNSIGNED_8BITS</name>
              </dimensionType>
            </coverageDimension>
            <coverageDimension>
              <name>Band3</name>
              <description>GridSampleDimension[1.0,255.0]</description>
              <range>
                <min>1.0</min>
                <max>255.0</max>
              </range>
              <nullValues>
                <double>0.0</double>
              </nullValues>
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
          <nativeCoverageName>GOES-18</nativeCoverageName>
        </coverage>
        '''
        return coverage