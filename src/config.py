import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class EventBusSettings:
    connection_string: str = os.environ.get('QUEUECONNECTION', None)
    upload_topic: str = os.environ.get('UPLOAD_TOPIC', None)
    upload_subscription: str = os.environ.get('UPLOAD_SUBSCRIPTION', None)
    validation_topic: str = os.environ.get('VALIDATION_TOPIC', None)
    container_name: str = os.environ.get('CONTAINER_NAME', 'osw')


class Settings(BaseSettings):
    app_name: str = 'python-osw-formatter'
    event_bus = EventBusSettings()
