import json
import logging

import azure.functions as func

from utils.azure_storage import AzureStorage


def main(message: func.ServiceBusMessage):
    # Log the Service Bus Message as plaintext

    message_content_type = message.content_type
    message_body = message.get_body().decode('utf-8')

    logging.info('Python ServiceBus topic trigger processed message.')
    logging.info('Message Content Type: %s', message_content_type)
    logging.info('Message Body: %s', message_body)

    url_parts = json.loads(message_body)['data']['url'].split('.blob.core.windows.net/')
    source_storage_account = url_parts[0][8:] # strip out leading https://
    file_parts = url_parts[1].split('/', 1)

    storage_client = AzureStorage(source_storage_account)
    storage_client.copy_file(
        source_container=file_parts[0],
        source_path=file_parts[1],
        destination_storage_acc='lhdatapoc',
        destination_container='testdatalake'
    )
