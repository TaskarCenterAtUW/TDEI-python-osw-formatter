import os
import psutil
from fastapi import FastAPI, APIRouter, Depends, status
from functools import lru_cache
from src.config import Settings
from src.service.osw_formatter_service import OSWFomatterService

app = FastAPI()
app.formatter_service = None

prefix_router = APIRouter(prefix='/health')


@lru_cache()
def get_settings():
    return Settings()


@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings)) -> None:
    try:
        print('<><> DL Directory <><>')
        set2 = Settings()
        print(set2.get_download_directory())
        
        dl_directory = set2.get_download_directory()
        if not os.path.exists(dl_directory):
            os.makedirs(dl_directory)
        app.formatter_service = OSWFomatterService()
        
    except Exception as e:
        print(e)
        print('\n\n\x1b[31m Application startup failed due to missing or invalid .env file \x1b[0m')
        print('\x1b[31m Please provide the valid .env file and .env file should contains following parameters\x1b[0m')
        print()
        print('\x1b[31m UPLOAD_TOPIC=xxxx \x1b[0m')
        print('\x1b[31m UPLOAD_SUBSCRIPTION=xxxx \x1b[0m')
        print('\x1b[31m VALIDATION_TOPIC=xxxx \x1b[0m')
        print('\x1b[31m QUEUECONNECTION=xxxx \x1b[0m')
        print('\x1b[31m STORAGECONNECTION=xxxx \x1b[0m \n\n')
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

@app.on_event('shutdown')
async def shutdown_event() -> None:
    print('Application is shutting down...')
    if app.formatter_service:
        app.formatter_service.stop_listening()

@app.get('/', status_code=status.HTTP_200_OK)
@prefix_router.get('/', status_code=status.HTTP_200_OK)
def root():
    return "I'm healthy !!"


@app.get('/ping', status_code=status.HTTP_200_OK)
@app.post('/ping', status_code=status.HTTP_200_OK)
@prefix_router.get('/ping', status_code=status.HTTP_200_OK)
@prefix_router.post('/ping', status_code=status.HTTP_200_OK)
def ping():
    return "I'm healthy !!"


app.include_router(prefix_router)
