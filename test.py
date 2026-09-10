import os
# Verify required EUMETSAT credentials are set
required_vars = ["EUMETSAT_PASS", "EUMETSAT_SECRET"]
missing = [env for env in required_vars if os.getenv(env) is None]
if missing:
    print(f'Warning: Missing required environment variables: {missing}')

import satellite
import goes_east
import goes_west
import h8
import msg_0
import msg_io

import time
from concurrent.futures import ThreadPoolExecutor

# Your satellite sources list
satellites = [
    goes_east.GOESEastDataSource(),
    goes_west.GOESWestDataSource(),
    msg_0.MSG0DegreeDataSource(),
    msg_io.MSGIndianOceanDataSource(),
    h8.Himawari8DataSource()
]

def fetch_data_for_satellite(satellite, file_prefix):
    """
    Wrapper function to call getRecentData on a satellite object.
    """
    satellite.getRecentData(file_prefix=file_prefix)

def main():
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
main()

print(satellites)

for sat in satellites :
    sat.toNetCDF()

# Update 'latest' symlink to point to the most recent output directory
latest_link = os.path.relpath('latest', os.environ["OUTPUT_DIR"])
latest_path = os.path.relpath(os.path.basename(satellite.Config.output_dir), os.eviron["OUTPUT_DIR"])
if os.path.islink(latest_link) or os.path.exists(latest_link):
    os.remove(latest_link)
os.symlink(latest_path, latest_link)

