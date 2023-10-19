import logging
from datetime import datetime, timedelta

import httpx
import requests
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn

class KNMI:
    
    API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImE1OGI5NGZmMDY5NDRhZDNhZjFkMDBmNDBmNTQyNjBkIiwiaCI6Im11cm11cjEyOCJ9"
    API_URL = "https://api.dataplatform.knmi.nl/open-data"
    API_VERSION = "v1"

    DATASET_NAME = "harmonie_arome_cy40_p1"
    DATASET_VERSION = "0.2"

    BASE_URL = f"{API_URL}/{API_VERSION}/datasets/{DATASET_NAME}/versions/{DATASET_VERSION}"

    FILE_PREFIX = "harm40_v1_p1_"
    FILE_FORMAT = "tar"

    _logger = logging.getLogger("weather.knmi")

    def __init__(self):
        # self._client = httpx.AsyncClient()
        pass
        

    def download(self, filename):
        """Download a file from the KNMI API."""

        self._logger.debug(f"Dataset file to download: {filename}")
        
        response = requests.get(
            url=f"{self.BASE_URL}/files/{filename}/url",
            headers={"Authorization": self.API_KEY}
        )

        if response.status_code != 200:
            self._logger.error("Unable to retrieve download url for file")
            self._logger.error(response.text)
            return None

        download_url = response.json().get("temporaryDownloadUrl")
        self._logger.info(f"Successfully retrieved temporary download URL for dataset file {filename}")
        
        # Check logging for deprecation
        if "X-KNMI-Deprecation" in response.headers:
            deprecation_message = response.headers.get("X-KNMI-Deprecation")
            self._logger.warning(f"Deprecation message: {deprecation_message}")


        try:
            with httpx.stream("GET", download_url) as response:
                total = int(response.headers["Content-Length"])

                with Progress(
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    BarColumn(bar_width=None),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                ) as progress:
                    task = progress.add_task("download", total=total)

                    with open(filename, "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                            progress.update(task, completed=response.num_bytes_downloaded)
        

        except Exception:
            self._logger.exception("Unable to download file using download URL")
            return

        self._logger.info(f"Successfully downloaded dataset file to {filename}")



    def latest_file_name(self):
        """Retrieve the latest file name."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        self._logger.debug(f"UTC now: {now}")
        self._logger.debug(f"UTC yesterday: {yesterday}")

        response = requests.get(
            url=f"{self.BASE_URL}/files/",
            headers={"Authorization": self.API_KEY},
            params={
                "maxKeys": 5,
                "startAfterFilename": self.date_as_filename(yesterday.year, yesterday.month, yesterday.day, yesterday.hour)
            }
        )

        if response.status_code != 200:
            self._logger.error("Unable to retrieve files from API")
            self._logger.error(response.text)
            return None

        files = response.json().get("files")
        if files is None or len(files) == 0:
            self._logger.error("No files found for dataset")
            return None

        self._logger.info(f"Retrieved latest file from API")
        latest = files[-1]
        return latest.get("filename")

    @classmethod
    def date_as_filename(cls, year, month, day, hours):
        if month < 10:
            month = f"0{month}"
        if day < 10:
            day = f"0{day}"
        if hours < 10:
            hours = f"0{hours}"
        return f"{cls.FILE_PREFIX}{year}{month}{day}{hours}.{cls.FILE_FORMAT}"
    

class File:

    def __init__(self, filename, url):
        self.filename = filename
        self.url = url
        self._logger = logging.getLogger("knmi.file")