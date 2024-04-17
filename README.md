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
https://github.com/hammad93/hurricane-map/issues/15

# Quickstart
  - The EUMETSAT provides free access to data but requires registration. from the following link and set the following environment variables
    - https://eoportal.eumetsat.int/userMgmt/register.faces
    - https://user.eumetsat.int/resources/user-guides/eumetsat-data-access-client-eumdac-guide
    - https://api.eumetsat.int/api-key/
    - https://gitlab.eumetsat.int/eumetlab/data-services/eumdac_data_store/-/blob/master/3_Downloading_products.ipynb?ref_type=heads
    - EUMETSAT_PASS
    - EUMETSAT_SECRET
  - SFTP environment variables to upload results
    - BASE64_SSH_GEOSERVER
      - A base 64 encoded string of the SSH key
    - HOST_SSH
    - USER_SSH