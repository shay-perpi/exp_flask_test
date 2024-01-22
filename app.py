import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
import matplotlib.pyplot as plt

from flask import Flask, request, Response
from tests.test_export import test_demi, send_requests, HandleCallback, logger, time_keeper
from common.config_file import export_count
import urllib3

urllib3.disable_warnings()
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)

request_count = 0
successful_exports = 0


def create_and_save_timeline(time_dict, successful_exports, received_exports):
    # Extract keys and values
    ids = list(time_dict.keys())
    times_seconds = [value.total_seconds() for value in time_dict.values()]

    # Round times to the nearest 30-second interval
    times_rounded = [round(time_sec / 30) * 30 for time_sec in times_seconds]

    # Create a dictionary to store the y-coordinate for each unique time
    y_coordinates = defaultdict(list)
    for i, time in enumerate(times_rounded):
        y_coordinates[time].append(i)

    # Plotting
    for time, indices in y_coordinates.items():
        if len(indices) == 1:
            plt.scatter([time], [0] * len(indices))  # Use the same y-coordinate for each point
        else:
            # Adjust vertical positions for overlapping times
            for i, index in enumerate(indices):
                plt.scatter([time], [i], label=f'Point {index + 1}' if i == 0 else None)  # Separate labels for overlapping points

    # Annotate each point with its ID above
    for i, txt in enumerate(ids):
        last_4_digits = str(txt)[-4:]
        plt.annotate(last_4_digits, (times_rounded[i], 0), textcoords="offset points", xytext=(0, 10), ha='center')

    # Add information to the side of the graph
    info_text = f'Successful Exports: {successful_exports}\nReceived Exports: {received_exports}'
    plt.text(1.02, 0.95, info_text, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

    plt.yticks([])  # Hide the Y-axis labels
    plt.xlabel('Time (seconds)')
    plt.title('Timeline of IDs (30-second intervals with adjusted positions for overlap)')
    plt.legend()

    file_path = os.path.join("/home/shayperp/PycharmProjects/exp_flask_tes/download", "export_callback_graph.png")
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()  # Close the plot to avoid displaying it
    print(f"Figure saved to: {file_path}")


def process_webhook(obj_download):
    try:
        global successful_exports
        logger.info("Processing {}".format(obj_download['id']))
        task = HandleCallback(obj_download)
        task.test_callback()
        successful_exports += 1
    except Exception as e:
        logger.error("Error processing {}".format(obj_download['id']))


@app.route('/webhook', methods=['POST'])
def webhook():
    global request_count
    request_count += 1
    print("webhook")
    logger.info("Webhook call back event")
    if request.method == 'POST':
        try:
            data_dict = dict(json.loads(request.data))
            time_keeper.keep_time_by_id(data_dict['data']['id'])
            future = executor.submit(process_webhook, data_dict['data'])
            if request_count == export_count:
                logger.info("All webhook responses submitted. Waiting for threads to finish.")
                # Wait for all threads to finish
                wait([future])

                logger.info("All threads finished. Generating timeline.")
                create_and_save_timeline(time_keeper.build_memory_dict(),successful_exports,request_count)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data ")

    return Response(request.data, headers={'Content-Type': 'application/json'}, status=200)


@app.route('/')
def index():
    # Ensure you are returning a valid response object, not None
    return 'Hello, World!'


if __name__ == '__main__':
    print("main")
    # test_demi()
    send_requests()
    app.run()
