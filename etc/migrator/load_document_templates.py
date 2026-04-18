import os
import logging

import requests


TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures/data/deps/document_templates"
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")

URL = os.getenv("FILE_STORAGE_URL")


def get_url(path):
    return "".join((URL, path)).rstrip("/")


def upload_file(filepath):
    path, filename = os.path.split(filepath)
    with open(filepath, "rb") as fp:
        resp = requests.post(
            get_url(path),
            files={"file": (filename, fp)},
            data={"replaceIfExists": True}
        )
    if resp.status_code != 200:
        logging.error(f"{filename} failed to upload: {resp.status_code}")


if __name__ == "__main__":

    try:
        for path, _, files in os.walk(TEMPLATES_DIR):
            # sequence of absolute paths to files in TEMPLATES_DIR and subdirs
            filepaths = (os.path.abspath(os.path.join(path, f)) for f in files)
            for filepath in filepaths:
                upload_file(filepath)

        logging.info("Finished uploading the documents' templates")
    except requests.exceptions.ConnectionError as exc:
        logging.info("Failed to connect to the file storage. URL: %s", URL)
