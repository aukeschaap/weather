import logging
import os
import sys
from datetime import datetime
from datetime import timedelta

import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.DEBUG))
logger.addHandler(logging.StreamHandler(sys.stdout))

API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImE1OGI5NGZmMDY5NDRhZDNhZjFkMDBmNDBmNTQyNjBkIiwiaCI6Im11cm11cjEyOCJ9"
API_URL = "https://api.dataplatform.knmi.nl/open-data"
API_VERSION = "v1"

dataset_name = "radar_reflectivity_composites"
dataset_version = "2.0"
file_prefix = "RAD_NL25_PCP_NA_"



def main():

    # Use get file to retrieve a file from one hour ago.
    # Filename format for this dataset equals KMDS__OPER_P___10M_OBS_L2_YYYYMMDDHHMM.nc,
    # where the minutes are increased in steps of 10.
    timestamp_now = datetime.utcnow()
    timestamp_one_hour_ago = timestamp_now - timedelta(hours=1) - timedelta(minutes=timestamp_now.minute % 10)
    logger.debug(f"Current time (UTC): {timestamp_now}")
    logger.debug(f"One hour ago (UTC): {timestamp_one_hour_ago}")

    response = requests.get(
        url=f"{API_URL}/{API_VERSION}/datasets/{dataset_name}/versions/{dataset_version}/files/",
        headers={"Authorization": API_KEY},
        params={
            "maxKeys": 15,
            "startAfterFilename": f"{file_prefix}{timestamp_one_hour_ago.strftime('%Y%m%d%H%M')}.nc"
        }
    )
    files = response.json().get("files")
    if files is None or len(files) == 0:
        logger.error("No files found for dataset")
        sys.exit(1)
    
    logger.info(f"Retrieved {len(response.json().get('files'))} files from API")
    latest = files[-1]
    filename = latest.get("filename")

    logger.debug(f"Dataset file to download: {filename}")
    response = requests.get(
        url=f"{API_URL}/{API_VERSION}/datasets/{dataset_name}/versions/{dataset_version}/files/{filename}/url",
        headers={"Authorization": API_KEY}
    )
    if response.status_code != 200:
        logger.error("Unable to retrieve download url for file")
        logger.error(response.text)
        sys.exit(1)

    logger.info(f"Successfully retrieved temporary download URL for dataset file {filename}")

    download_url = response.json().get("temporaryDownloadUrl")
    # Check logging for deprecation
    if "X-KNMI-Deprecation" in response.headers:
        deprecation_message = response.headers.get("X-KNMI-Deprecation")
        logger.warning(f"Deprecation message: {deprecation_message}")

    download_file_from_temporary_download_url(download_url, filename)


def download_file_from_temporary_download_url(download_url, filename):
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception:
        logger.exception("Unable to download file using download URL")
        sys.exit(1)

    logger.info(f"Successfully downloaded dataset file to {filename}")


if __name__ == "__main__":
    main()