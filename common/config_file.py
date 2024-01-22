import os
import json


environment = os.getenv("environment")
token = os.getenv("token","eyJhbGciOiJSUzI1NiIsImtpZCI6Im1hcC1jb2xvbmllcy1pbnQifQ.eyJhbyI6WyJodHRwczovL2FwcC1pbnQtY2xpZW50LXJvdXRlLWludGVncmF0aW9uLmFwcHMuajFsazNuanAuZWFzdHVzLmFyb2FwcC5pbyIsImh0dHBzOi8vYXBwLWludC1jbGllbnQtdG9vbHMtcm91dGUtaW50ZWdyYXRpb24uYXBwcy5qMWxrM25qcC5lYXN0dXMuYXJvYXBwLmlvIiwiaHR0cDovL2xvY2FsaG9zdDozMDAwIl0sImQiOlsicmFzdGVyIiwicmFzdGVyV21zIiwicmFzdGVyRXhwb3J0IiwiZGVtIiwidmVjdG9yIiwiM2QiXSwiaWF0IjoxNjc0NjMyMzQ2LCJzdWIiOiJtYXBjb2xvbmllcy1hcHAiLCJpc3MiOiJtYXBjb2xvbmllcy10b2tlbi1jbGkifQ.e-4SmHNOE8FwpcJoHdp-3Dh6D8GqCwM5wZfZIPrivGhfeKdihcsjEj_WN2jWN-ULha_ytZN5gRusLjwikNwgbF6hvb-QTDe3bEHPAjtgpZmF4HaJze8e6VPDF1tTC52CHDzNnwkUGAH1tnVGq10SnyhsGDezUChTVeBeVu-swTI58qCjemUQRw7-Q03uSEH24AkbX2CC1_rNwulo7ChglyTdn01tTWPsPjIuDjeixxm2CUmUHpfZzroaSzwof7ByQe22o3tFddje6ItNLBUC_VN7UfNLa_QPSVbIuNac-iMGFbK-RIyXUK8mp1AwddvSGsBUYcDs8fWMLzKhItljnw")
raster_url = os.getenv("url","https://export-management-export-management-route-no-auth-integration.apps.j1lk3njp.eastus.aroapp.io")
ca_file = os.getenv("certification", None)
domain = os.getenv("domain", "RASTER")
record_id = os.getenv("record_id", "dcf8f87e-f02d-4b7a-bf7b-c8b64b2d202a")
trigger_task_create = os.getenv("trigger_task_create", "export-tasks")
required_resolution = os.getenv("required_resolution", 0.0000013411)
headers = os.getenv("headers", {"Content-Type": "application/json"})
export_count = os.getenv("export_count", 6)

foot_print_file = os.getenv("foot_prints_file", "footprints.txt")
path_dir = os.getenv("path_export_dir_raster")
foot_print_demi = os.getenv("foot_print_demi", [[35.171864081, 32.272985262], [35.197864081, 32.272985262], [35.197864081, 32.254985262], [35.171864081, 32.254985262], [35.171864081, 32.272985262]])
url_trigger = f"{raster_url}/{trigger_task_create}?token={token}"
path_download = os.getenv("path_to_products", "/home/shayperp/PycharmProjects/exp_flask_tes/download")
path_log = os.getenv("logger_path", None) or "/home/shayperp/PycharmProjects/exp_flask_tes/log"
logger_name = os.getenv("logger_name", "export-test")
json_file_path = os.getenv(
    "export_config") or "/home/shayperp/PycharmProjects/pythonProject/export_scadolar_config/scadolar_config.json"
callback_url = os.getenv("callback_url", "https://d777-2a0d-6fc0-2a60-4100-da3a-7c38-1c8a-bd8.ngrok-free.app/webhook")


def create_data_export(record_id: str, foot_prints, resolution: float, domain: str):
    json_interface = {
        "catalogRecordID": record_id,
        "domain": domain,
        "ROI": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"maxResolutionDeg": resolution},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [foot_prints]
                    }
                }
            ]
        },
        "artifactCRS": "4326",
        "description": "string",
        "keywords": {
            "foo": "ExportTest"
        },
        "parameters": {
            "foo": "ExportTest"
        },
        "webhook": [
            {
                "events": [
                    "TASK_COMPLETED"
                ],
                "url": callback_url
            }
        ]
    }
    return json.dumps(json_interface, indent=2)
