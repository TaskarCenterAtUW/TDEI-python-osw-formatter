import os
from python_ms_core import Core

core = Core()

storage_client = core.get_storage_client()
container_name = 'osw'

dir = os.path.dirname(__file__)
TEST_FILE = os.path.join(dir, 'downloads/c8c76e89f30944d2b2abd2491bd95345.graph.osm.xml')
print(TEST_FILE)
container = storage_client.get_container(container_name=container_name)
remote_path = f'test/test123.xml'
file = container.create_file(remote_path)
print('start uploading')
with open(TEST_FILE, "rb") as data:
    file.upload(data)
print('done uploading')
print(file.get_remote_url())