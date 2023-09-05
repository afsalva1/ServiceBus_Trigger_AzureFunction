import json
import logging

import azure.functions as func
from utils.azure_storage import AzureStorage

def main(event: func.EventGridEvent):
    data = event.get_json()
    result = json.dumps({
        'id': event.id,
        'data': data,
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger starting processing an event: %s', result)

    url_parts = data['url'].split('.blob.core.windows.net/')
    source_storage_account = url_parts[0][8:] # strip out leading https://
    file_parts = url_parts[1].split('/', 1)

    storage_client = AzureStorage(source_storage_account)
    storage_client.copy_file(
        source_container=file_parts[0],
        source_path=file_parts[1],
        destination_storage_acc='lhdatapoc',
        destination_container='testdatalake'
    )

    logging.info('Python EventGrid trigger finished processing an event: %s', result)
