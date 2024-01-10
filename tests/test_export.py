# test_main.py
import ast
import json
import os
import ssl
import rasterio
import subprocess
from time_handler import TimeHandler
import pytest
import requests
from flask.testing import FlaskClient
from common.log import LoggerSingleton
from common.config_file import raster_url, trigger_task_create, token, create_data_export, record_id, foot_print_demi, \
    required_resolution, domain, foot_print_file, ca_file, path_download
from app import app

logger = LoggerSingleton()
time_keeper = TimeHandler()


def trigger_missing_params():
    logger.info(f"Start {trigger_missing_params.__name__}")
    url_export = f"{raster_url}/{trigger_task_create}?token={token}"
    trigger_params = create_data_export(record_id=record_id, foot_prints=foot_print_demi,
                                        resolution=required_resolution, domain=domain)
    trigger_params['catalogRecordID'] = ""
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing Id_Record ")

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, "")
    trigger_params['domain'] = ""
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing Domain ")

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, domain)
    trigger_params['ROI']['features'] = []
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing features ")

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, domain)
    req = requests.post(url=f"{raster_url}/{trigger_task_create}", data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code >= 400, logger.error("Request succeeded despite missing token ")

    logger.info(f" End successfully  {trigger_missing_params.__name__}")


def trigger_invalid_params():
    logger.info(f"Start {trigger_invalid_params.__name__}")
    url_export = f"{raster_url}/{trigger_task_create}?token={token}"

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, domain=domain)
    trigger_params['catalogRecordID'] = "132456789789789"
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing Id_Record ")

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, domain=domain)
    trigger_params['domain'] = "rs"
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing Domain ")

    trigger_params = create_data_export(record_id, foot_print_demi, required_resolution, domain=domain)
    trigger_params['ROI']['features'] = [{"C": "D"}]
    req = requests.post(url=url_export, data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code > 204, logger.error("Request succeeded despite missing features ")

    trigger_params = create_data_export(record_id=record_id, foot_prints=foot_print_demi,
                                        resolution=required_resolution, domain=domain)
    wrong_token = "123"
    req = requests.post(url=f"{raster_url}/{trigger_task_create}?token={wrong_token}", data=trigger_params,
                        headers={"Content-Type": "application/json"})
    assert req.status_code >= 400, logger.error("Request succeeded despite missing features ")

    logger.info(f" End successfully  {trigger_invalid_params.__name__}")


def test_demi():
    logger.info("Start Test : ")

    trigger_missing_params()
    trigger_invalid_params()


def send_requests():
    params = list_of_params_requests()
    for data in params:
        try:
            req = requests.post(url=raster_url, data=data,
                                headers={"Content-Type": "application/json"})
            req.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
            time_keeper.keep_time_by_id(req.json()["data"]["id"])  # keep the time from the response of the request
            logger.info(f"Request for {data} successful. Response: {req.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending request {data}: {e}")


def list_of_params_requests(export_count=1):
    list_of_params = []
    with open(foot_print_file, 'r') as file:
        for i in range(export_count):
            foot_print = file.readline()
            foot_pr = ast.literal_eval(foot_print)
            param = create_data_export(record_id=record_id, foot_prints=foot_pr, resolution=required_resolution,
                                       domain=domain)
            list_of_params.append(param)
    return list_of_params


@pytest.fixture
def client() -> FlaskClient:
    with app.test_client() as client:
        yield client


def callback(client):
    response = client.get('/webhook')
    print("Fixture")
    assert response.status_code == 200
    time_keeper.keep_time_by_id(response.json()['data']['id'])  # keep the time from the callback

    assert b'Hello, World!' in response.data


class StopThread(Exception):
    pass


class HandleCallback:
    def __init__(self, response):
        self.params = response

    def __download_product(self, url, file_name):
        path = f"{path_download}/{file_name}"
        try:
            d = path_download + '/' + file_name
            subprocess.check_call(['wget', '--no-check-certificate', '-O', d, url])
            return d
        except Exception as e:  # except StopThread as e:
            logger.error(f"Download operation failed {e}")
            return False

    def test_callback(self):
        assert self.params['catalogRecordID'], logger.error(" Not catalog id in response trigger ")
        assert self.params['domain'] == domain, logger.error(" Not domain in response trigger ")
        assert self.params['ROI'], logger.error(" Not ROI in response trigger ")
        assert self.params['artifactCRS'], logger.error(" Not artifactCRS in response trigger ")
        assert self.params['webhook'], logger.error(" Not webhook id in response trigger ")
        assert self.params['artifacts'], logger.error("Not artifacts in response ")
        self.__test_status_api()
        self.__metadata()
        self.__products()

    def __test_status_api(self):
        url_export_status = f"{raster_url}/{trigger_task_create}/{self.params['id']}?token={token}"
        response = requests.get(url=url_export_status, headers={"Content-Type": "application/json"}, verify=False)
        response.raise_for_status()
        assert response.json()["progress"] == 100

    def __metadata(self):
        # logger.info(f"Enter {self.metadata.__name__}")
        assert self.params['artifacts'][1], "No Metadata info in response"
        metadata_request = self.params['artifacts'][1]
        assert metadata_request, logger.error("Not metadata")
        metadata = requests.get(metadata_request['url'], verify=False)
        assert metadata, logger.error("Not JSON in MetaData")
        assert len(metadata.content) == metadata_request['size'], "The Metadata size not much as request data"
        logger.info(str(metadata.content))
        # logger.info(f"End successfully {self.metadata.__name__}")

    def __products(self):
        # logger.info(f"Enter {self.products.__name__}")
        assert self.params['artifacts'][0], logger.error("No product info  in response")
        product = self.params['artifacts'][0]
        assert product['url'], logger.error(" No Url in artifacts product")
        assert product['size'], logger.error(" No Size in artifacts product")
        assert product['name'], logger.error(" No Name in artifacts product")
        assert product['type'], logger.error(" No Type in artifacts product")
        # resp = wget.download(product['url'], out=path_dir)
        path = self.__download_product(product["url"], product["name"])

        assert path, logger.error(" Response of product download ERROR ")
        logger.info(str(path))
        try:
            dataset = rasterio.open(path, mode='r')
        except Exception as E:
            logger.info("Cannot open product: " + str(E))
        assert os.path.getsize(path) == int(product['size']), logger.error(" Size not match metadata to product")

