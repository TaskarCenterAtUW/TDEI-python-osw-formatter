import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class EventBusSettings:
    connection_string: str = os.environ.get('QUEUECONNECTION', None)
    validation_topic: str = os.environ.get('FORMATTER_TOPIC', None)
    validation_subscription: str = os.environ.get('FORMATTER_SUBSCRIPTION', None)
    formatter_topic: str = os.environ.get('FORMATTER_UPLOAD_TOPIC', None)
    container_name: str = os.environ.get('CONTAINER_NAME', 'osw')


# /Users/nareshd/Documents/tdei/repo/TDEI-python-osw-formatter/downloads
class Settings(BaseSettings):
    app_name: str = 'python-osw-formatter'
    event_bus = EventBusSettings()
    max_concurrent_messages: int = int(os.environ.get('MAX_CONCURRENT_MESSAGES', 1))
    # Single-run worker should consume one message and then shut down.
    max_receivable_messages: int = int(os.environ.get('MAX_RECEIVABLE_MESSAGES', 1))
    # Wait for queue message completion/abandon settlement before terminating process.
    message_settle_wait_seconds: float = float(os.environ.get('MESSAGE_SETTLE_WAIT_SECONDS', 10.0))
    # Delay gives queue client time to settle/complete the in-flight message before exit.
    shutdown_delay_seconds: float = float(os.environ.get('SHUTDOWN_DELAY_SECONDS', 2.0))

    def get_root_directory(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    def get_download_directory(self) -> str:
        root_dir = self.get_root_directory()
        parent_dir = os.path.dirname(root_dir)
        return os.path.join(parent_dir, 'downloads')
