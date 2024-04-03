class MSG0DegreeDataSource(DataSource):
    def __init__(self):
        self.consumer_key = Config.eumetsat_consumer_key
        self.consumer_secret = Config.eumetsat_consumer_secret

    def getRecentData(self, file_prefix=''):
        """
        Fetch the most recent data from EUMETSAT

        :param file_prefix: Optional. A string to prepend to the filename on save.
        """
        credentials = (self.consumer_key, self.consumer_secret)
        token = eumdac.AccessToken(credentials)

        print(f"This token '{token}' expires {token.expiration}")

        collection = 'EO:EUM:DAT:MSG:HRSEVIRI'
        datastore = eumdac.DataStore(token)
        selected_collection = datastore.get_collection(collection)
        print(selected_collection.title)

        display(selected_collection.search_options)

        product = selected_collection.search().first()
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
            print(f"Error related to the product '{product}' while trying to download it: '{error.msg}'")
        except requests.exceptions.ConnectionError as error:
            print(f"Error related to the connection: '{error.msg}'")
        except requests.exceptions.RequestException as error:
            print(f"Unexpected error: {error}")

    def toNetCDF(self, existing_netcdf_path=None):
        '''
        References
        ----------
        https://satpy.readthedocs.io/en/stable/api/satpy.scene.html
        '''
        # read in the .nat
        scn = Scene(
            filenames=[self.recent_path],
            reader='seviri_l1b_native')
        # output to NetCDF
        output = scn.load(scn.available_dataset_names(), upper_right_corner='NE')
        scn.save_datasets(
            writer="cf",
            groups={
                'default': filter(lambda x: x!='HRV', scn.available_dataset_names()),
                'hrv': ['HRV']})
        print(f"Transformed {self.recent_path} into a NetCDF.")
        pass
