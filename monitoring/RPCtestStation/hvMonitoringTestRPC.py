
from influxdb_client import InfluxDBClient

url = 'https://dbod-labstrada.cern.ch:8097'
database = "labstrada"
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'
username="admin"
password="changeme"

client = InfluxDBClient(url=url, token=f'{username}:{password}', org='-', verify_ssl=True, ssl_ca_cert='/etc/ssl/certs/CERN-bundle.pem')

client.ping()