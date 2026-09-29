import os, shutil
import satellite
import goes_east
import goes_west
import h8
import msg_0
import msg_io
import fire
import time
from concurrent.futures import ThreadPoolExecutor

def fetch_data_for_satellite(satellite, file_prefix):
    """
    Wrapper function to call getRecentData on a satellite object.
    """
    satellite.getRecentData(file_prefix=file_prefix)

def download(satellites):
    prefix = f"[{int(time.time())}]"
    # Use ThreadPoolExecutor to run getRecentData concurrently for each satellite
    with ThreadPoolExecutor(max_workers=len(satellites)) as executor:
        # Schedule the executions
        futures = [executor.submit(fetch_data_for_satellite, satellite, prefix) for satellite in satellites]

        # Optionally, wait for all futures to complete and handle results/errors
        for future in futures:
            try:
                # Result handling here if needed
                future.result()  # This will raise exceptions if any occurred
            except Exception as e:
                print(f"An error occurred: {e}")
def check_envs(required_vars):
    missing = [env for env in required_vars if os.getenv(env) is None]
    if missing:
        print(f'Warning: Missing required environment variables: {missing}')
    return missing
def main(clean=0, wms=False):
    '''
    :param clean: Integer number of days to remove previous output
    :param wms: Update WMS based on output
    :return:
    '''
    # Verify required EUMETSAT credentials are set
    check_envs(["EUMETSAT_PASS", "EUMETSAT_SECRET"])
    # Your satellite sources list
    satellites = [
        goes_east.GOESEastDataSource(),
        goes_west.GOESWestDataSource(),
        msg_0.MSG0DegreeDataSource(),
        msg_io.MSGIndianOceanDataSource(),
        h8.Himawari8DataSource()
    ]
    print(satellites)
    download(satellites)
    # convert download into compatible NetCDF
    for sat in satellites:
        sat.toNetCDF()
    # update commands
    if clean:
        print('Removing previous output older than a day . . .')
        # remove previous output older than a day
        days = 1
        threshold = satellite.Config.timestamp - (60 * 60 * days)
        # Outputs are in the form:
        # hurricane-satellites-1790561025
        # hurricane-satellites-1790562587
        # :
        # .
        for output in os.listdir(satellite.Config.output_base):
            if 'hurricane-satellites' in output:
                output_path = os.path.join(satellite.Config.output_base, output)
                output_timestamp = int(output.split('-')[-1])
                if output_timestamp < threshold: # more than a day old
                    print(f'Removing {output_path} . . . ', end='')
                    shutil.rmtree(output_path)
                    print('Done')
        print('Done with removing previous output(s)')
    # update wms layers
    if wms:
        # workspace can be 'primary' on most installs
        env_check = check_envs(['GEOSERVER_WORKSPACE', 'GEOSERVER_URL',
                                'GEOSERVER_ADMIN_USER', 'GEOSERVER_ADMIN_PASSWORD'])
        if env_check:
            print(f"Unable to update WMS layers. Missing environment variables: {env_check}")
        else:
            print("Updating WMS . . .")
            for sat in satellites:
                # access class function to update/create
                sat.createLayer()
    pass
if __name__ == "__main__":
    fire.Fire(main)
