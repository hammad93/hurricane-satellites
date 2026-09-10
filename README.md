# hurricane-satellites
A repository for creating near real time meteorological satellite imagery for the purpose of visualizing outputs created by deep learning forecasts for tropical storms and hurricanes.

# Global Image
Consisting of the following satellites,
- GOES East
- GOES West
- MSG 0 Degree
- MSG Indian Ocean
- Himawari 8

Downloads must be from a primary source.

# References
- https://github.com/hammad93/hurricane-map/issues/15
- https://gitlab.eumetsat.int/eumetlab/data-services/eumdac_data_store/-/blob/master/3_Downloading_products.ipynb?ref_type=heads


# Quickstart
  - The EUMETSAT provides free access to data but requires registration. from the following link and set the following environment variables
    - EUMETSAT_PASS
      - This is the Consumer key
    - EUMETSAT_SECRET
      - This is the Consumer secret
    - API Token's are generated at runtime using the consumer key and secret
    - https://eoportal.eumetsat.int/userMgmt/register.faces
    - https://user.eumetsat.int/resources/user-guides/eumetsat-data-access-client-eumdac-guide
    - https://api.eumetsat.int/api-key/
  - Docker usage:
    - Build the image: `docker build -t hurricane-satellites docker/`
    - Run the automation: `docker run -v ./test:/output -e EUMETSAT_PASS= -e EUMETSAT_SECRET= hurricane-satellites`
        - If EUMETSAT variables are not set, Meteosat satellites will not be available.
