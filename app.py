import json
from datetime import datetime

from flask import Flask, request, Response
from tests.test_export import test_demi, send_requests, HandleCallback, logger, time_keeper
from common.config_file import export_count

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook")
    logger.info("Webhook call back event")
    if request.method == 'POST':
        try:
            data_dict = dict(json.loads(request.data))
            time_keeper.keep_time_by_id(data_dict['data']['id'])
            response = HandleCallback(data_dict['data'])
            response.test_callback()

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data ")

    return Response(request.data, headers={'Content-Type': 'application/json'}, status=200)

if __name__ == '__main__':
    test_demi()
    send_requests()
    app.run()
