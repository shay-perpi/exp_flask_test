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
    required_resolution, domain, foot_print_file, ca_file, path_download, export_count, token, url_trigger

logger = LoggerSingleton()
time_keeper = TimeHandler()


def trigger_missing_params():
    print("Test missing_params")

    logger.info(f"Start {trigger_missing_params.__name__}")
    url_export = url_trigger
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
    print("invalid_params")
    logger.info(f"Start {trigger_invalid_params.__name__}")
    url_export = url_trigger

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
    print("Test demi")

    logger.info("Start Test : ")

    trigger_missing_params()
    trigger_invalid_params()


def send_requests():
    time_keeper.set_start_time()

    url_export = url_trigger

    print("send requests")
    params = list_of_params_requests(export_count)
    for data in params:
        try:
            req = requests.post(url=url_export, data=data,
                                headers={"Content-Type": "application/json"}, verify=False)
            print(f"status: {req.status_code}\n  requets :{req.text} \n requests {req}")
            # response = json.loads(req.text)
            req.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
            request_id = req.json()["id"]
            time_keeper.keep_time_by_id(request_id)  # keep the time from the response of the request
            logger.info(f"Request for {request_id} ")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending request {data}: {e}")


def list_of_params_requests(export_count_e=1):
    list_of_params = []
    with open(foot_print_file, 'r') as file:
        for i in range(export_count_e):
            foot_print = file.readline()
            foot_pr = ast.literal_eval(foot_print)
            param = create_data_export(record_id=record_id, foot_prints=foot_pr, resolution=required_resolution,
                                       domain=domain)
            list_of_params.append(param)
    return list_of_params


class StopThread(Exception):
    pass


class HandleCallback:
    def __init__(self, response):
        self.params = response
        self.gpkg_path = None

    def __download_product(self, url, file_name):
        logger.info(f"Start download {file_name}")
        path = f"{path_download}/{file_name}"
        try:
            d = path_download + '/' + file_name
            subprocess.check_call(['wget', '--no-check-certificate', '-O', d, url])
            logger.info(f"Download {file_name} successfully")

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
        self.__delete_file()
        logger.info("Test end product")

    def __test_status_api(self):
        logger.info(f"Enter test_status_api")
        if token:
            url_export_status = f"{raster_url}/{trigger_task_create}/{self.params['id']}?token={token}"
        else:
            url_export_status = f"{raster_url}/{trigger_task_create}/{self.params['id']}"
        response = requests.get(url=url_export_status, headers={"Content-Type": "application/json"}, verify=False)
        response.raise_for_status()
        print(response.text)
        assert response.json()["progress"] == 100, logger.error("API progress not correct. ")
        logger.info(f"End successfully test_status_api")

    def __metadata(self):
        logger.info(f"Enter test Metadata")
        assert self.params['artifacts'][1], "No Metadata info in response"
        metadata_request = self.params['artifacts'][1]
        assert metadata_request, logger.error("Not metadata")
        metadata = requests.get(metadata_request['url'], verify=False)
        assert metadata, logger.error("Not JSON in MetaData")
        assert len(metadata.content) == metadata_request['size'], "The Metadata size not much as request data"
        logger.info(str(metadata.content))
        logger.info(f"End successfully test Metadata")

    def __products(self):
        logger.info(f"Enter tests products")
        assert self.params['artifacts'][0], logger.error("No product info  in response")
        product = self.params['artifacts'][0]
        assert product['url'], logger.error(" No Url in artifacts product")
        assert product['size'], logger.error(" No Size in artifacts product")
        assert product['name'], logger.error(" No Name in artifacts product")
        assert product['type'], logger.error(" No Type in artifacts product")
        self.gpkg_path = self.__download_product(product["url"], product["name"])
        print(self.gpkg_path)
        assert self.gpkg_path, logger.error(" Response of product download ERROR ")
        try:
            dataset = rasterio.open(self.gpkg_path, mode='r')
        except Exception as E:
            logger.info("Cannot open product: " + str(E))
        assert os.path.getsize(self.gpkg_path) == int(product['size']), logger.error(" Size not match metadata to product")
        logger.info(f"End successfully tests products")

    def __delete_file(self):
        file_path = self.gpkg_path
        logger.info(f"Enter Delete function with :  {file_path}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                # shutil.rmtree(file_path)
                logger.info(f"File {file_path} deleted successfully.")
            except PermissionError:
                logger.error(f"Permission error: Unable to delete {file_path}.")
            except Exception as e:
                logger.error(f"An error occurred: {e}")
        else:
            logger.error(f"File {file_path} does not exist.")
