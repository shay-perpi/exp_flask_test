import os
import json


environment = os.getenv("environment")
token = os.getenv("token","eyJhbGciOiJSUzI1NiIsImtpZCI6Im1hcC1jb2xvbmllcy1pbnQifQ.eyJkIjpbInJhc3RlciIsInJhc3RlcldtcyIsInJhc3RlckV4cG9ydCIsImRlbSIsInZlY3RvciIsIjNkIl0sImlhdCI6MTY3NDYzMjM0Niwic3ViIjoibWFwY29sb25pZXMtYXBwIiwiaXNzIjoibWFwY29sb25pZXMtdG9rZW4tY2xpIn0.D1u28gFlxf_Z1bzIiRHZonUgrdWwhZy8DtmQj15cIzaABRUrGV2n_OJlgWTuNfrao0SbUZb_s0_qUUW6Gz_zO3ET2bVx5xQjBu0CaIWdmUPDjEYr6tw-eZx8EjFFIyq3rs-Fo0daVY9cX1B2aGW_GeJir1oMnJUURhABYRoh60azzl_utee9UdhDpnr_QElNtzJZIKogngsxCWp7tI7wkTuNCBaQM7aLEcymk0ktxlWEAt1E0nGt1R-bx-HnPeeQyZlxx4UQ1nuYTijpz7N8poaCCExOFeafj9T7megv2BzTrKWgfM1eai8srSgNa3I5wKuW0EyYnGZxdbJe8aseZg")
raster_url = os.getenv("url","https://export-management-export-management-route-no-auth-integration.apps.j1lk3njp.eastus.aroapp.io")
ca_file = os.getenv("certification", None)
domain = os.getenv("domain", "RASTER")
record_id = os.getenv("record_id", "045eaa61-8f61-48d3-a240-4b02a683eca3")
trigger_task_create = os.getenv("trigger_task_create", "export-tasks")
required_resolution = os.getenv("required_resolution", 0.0000013411)
headers = os.getenv("headers", {"Content-Type": "application/json"})
export_count = os.getenv("export_count", 1)
pg_credential = os.getenv("pg_credential") or {
        "pg_host": "10.0.4.4",
        "pg_user": "postgres",
        "pg_port": "5432",
        "pg_pass": "Libot4allnonprod",
        "pg_job_task_table": "common-job-manager-q3-1-2023",
        "pg_pycsw_record_table": "raster-qa",
        "pg_mapproxy_table": "raster-qa",
        "pg_agent_table": "raster-qa"
    }

foot_print_file = os.getenv("foot_prints_file")
path_dir = os.getenv("path_export_dir_raster")
foot_print_demi = os.getenv("foot_print_demi", [[35.171864081, 32.272985262], [35.197864081, 32.272985262], [35.197864081, 32.254985262], [35.171864081, 32.254985262], [35.171864081, 32.272985262]])
url_trigger = f"{raster_url}/{trigger_task_create}?token={token}"
path_download = os.getenv("path_to_products",
                          "/home/shayperp/PycharmProjects/pythonProject/export_scadolar_config/product")
path_log = os.getenv("logger_path") or "../log"
logger_name = os.getenv("logger_name", "export-callback-service")
json_file_path = os.getenv(
    "export_config") or "/home/shayperp/PycharmProjects/pythonProject/export_scadolar_config/scadolar_config.json"
callback_url = os.getenv("callback_url")


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
    return json_interface
