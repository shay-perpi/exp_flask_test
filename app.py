import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from flask import Flask, request, Response
from tests.test_export import test_demi, send_requests, HandleCallback, logger, time_keeper
from common.config_file import export_count

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)

request_count = 0


@app.before_request
def before_request():
    global request_count
    request_count += 1


@app.after_request
def after_request(response):
    # Log information about the request
    if request_count == export_count:
        print(time_keeper.get_start_time())
        print(time_keeper.build_memory_dict())


def process_webhook(obj_download):
    try:
        logger.info("Processing {}".format(obj_download['id']))
        task = HandleCallback(obj_download)
        task.test_callback()
        logger.info("Finished processing {}".format(obj_download['id']))
    except Exception as e:
        logger.error("Error processing {}".format(obj_download['id']))


@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook")
    logger.info("Webhook call back event")
    if request.method == 'POST':
        try:
            data_dict = dict(json.loads(request.data))
            time_keeper.keep_time_by_id(data_dict['data']['id'])
            executor.submit(process_webhook, data_dict['data'])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data ")
    print(time_keeper.build_memory_dict())
    return Response(request.data, headers={'Content-Type': 'application/json'}, status=200)


if __name__ == '__main__':
    print("main")
    # test_demi()
    send_requests()
    app.run()
