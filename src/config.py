import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class EventBusSettings:
    connection_string: str = os.environ.get('QUEUECONNECTION', None)
    validation_topic: str = os.environ.get('VALIDATION_TOPIC', None)
    validation_subscription: str = os.environ.get('VALIDATION_SUBSCRIPTION', None)
    formatter_topic: str = os.environ.get('FORMATTER_TOPIC', None)
    container_name: str = os.environ.get('CONTAINER_NAME', 'osw')


# /Users/nareshd/Documents/tdei/repo/TDEI-python-osw-formatter/downloads
class Settings(BaseSettings):
    app_name: str = 'python-osw-formatter'
    event_bus = EventBusSettings()

    def get_root_directory(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    def get_download_directory(self) -> str:
        root_dir = self.get_root_directory()
        parent_dir = os.path.dirname(root_dir)
        return os.path.join(parent_dir, 'downloads')
