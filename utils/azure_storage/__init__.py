from typing import Dict
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeDirectoryClient, DataLakeFileClient, DataLakeServiceClient, FileSystemClient, PathProperties

class AzureStorage:
    def __init__(self, storage_account_name: str, storage_account_key: str = None):
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.service_client = DataLakeServiceClient(account_url=f'https://{storage_account_name}.dfs.core.windows.net', credential=storage_account_key or DefaultAzureCredential())
        self.file_system_clients: Dict[str, FileSystemClient] = {}
        self.directory_clients: Dict[str, DataLakeDirectoryClient] = {}

    def _get_file_system(self, file_system: str) -> FileSystemClient:
        if file_system not in self.file_system_clients:
            self.file_system_clients[file_system] = self.service_client.get_file_system_client(file_system=file_system)
        return self.file_system_clients[file_system]

    def _get_directory_client(self, file_system: str, directory: str) -> DataLakeDirectoryClient:
        file_system_client = self._get_file_system(file_system)
        key = f'{file_system}_{directory}'
        if directory not in self.directory_clients:
            self.directory_clients[key] = file_system_client.get_directory_client(directory)
        return self.directory_clients[key]

    def _get_data_lake_file_client(self, data_lake_client: DataLakeServiceClient, file_system: str, file_path: str) -> DataLakeFileClient:
        return data_lake_client.get_file_client(file_system, file_path)

    def upload_file(self, data, file_system, directory, file_name):
        directory_client = self._get_directory_client(file_system, directory)
        file_client = directory_client.create_file(file_name)
        file_client.append_data(data, offset=0, length=len(data))
        file_client.flush_data(len(data))

    def list_directory_contents(self, file_system, file_path) -> PathProperties:
        file_system_client = self._get_file_system(file_system)
        return file_system_client.get_paths(path=file_path)

    def download_file_contents(self, file_system, file_name):
        file_system_client = self._get_file_system(file_system)
        return file_system_client.get_file_client(file_name).download_file().readall()

    def copy_file(self, source_container: str, source_path: str, destination_storage_acc: str, destination_container: str) -> None:
        source_file = self._get_data_lake_file_client(self.service_client, source_container, source_path)

        # Make sure the source blob exists before attempting to copy
        if source_file.exists():
            source_file_properties = source_file.get_file_properties()

            if destination_storage_acc != self.storage_account_name:
                dest_data_lake_service_client = DataLakeServiceClient(account_url=f'https://{destination_storage_acc}.dfs.core.windows.net', credential=DefaultAzureCredential())
            else:
                dest_data_lake_service_client = self.service_client
            destination_file_client = self._get_data_lake_file_client(dest_data_lake_service_client, destination_container, f'{source_container}/{source_path}')
            destination_file_client.create_file(source_file_properties.content_settings, source_file_properties.metadata)
            destination_file_client.upload_data(source_file.download_file(), source_file_properties.size, True)

            # Get the destination blob properties
            destination_file_properties = destination_file_client.get_file_properties()
            print(f"Total bytes copied: {destination_file_properties.size}")
