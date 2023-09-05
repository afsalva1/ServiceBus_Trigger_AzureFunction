from setuptools import setup

setup(
    name='common',
    version='0.0.1',
    packages=[
        'azure_storage'
    ],
    install_requires=[
        'azure-functions',
        'azure-identity',
        'azure-storage-file-datalake'
    ],
    python_requires='>=3.7'
)
