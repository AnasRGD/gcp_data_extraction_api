import os
import datetime
import pendulum
import json
import requests
import pandas as pd

from pathlib import Path

from google.cloud import storage
from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator



def get_weather_data_from_api(cities):
    api_key = "6092402787f9f4206afa86aa168f6df4"

    for city in cities:
        url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s" % (city, api_key)

        response = requests.get(url)
        data = json.loads(response.text)
        df = pd.json_normalize(data)

        #print(df)

        dirname = Path(__file__).absolute().parent
        pathfile = os.path.join(dirname, 'weatherData.csv')
        print('The path is : '+ pathfile)
        if not os.path.isfile(pathfile):
            df.to_csv(pathfile,header=True, index=False)
        else: # else it exists so append without writing the header
            df.to_csv(pathfile, mode='a', header=False, index=False)


def upload_to_bucket(bucket_name="ar-data-extraction-backup", destination_blob_name="dags/open-api-extract/weatherData.csv"):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # 
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    dirname = Path(__file__).absolute().parent
    pathfile = os.path.join(dirname, 'weatherData.csv')


    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(pathfile)

    print(
        f"File {pathfile} uploaded to {destination_blob_name}."
    )

local_tz = pendulum.timezone("Europe/Paris")
default_dag_args = {
    'start_date': datetime.datetime(2020, 3, 30, tzinfo=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': datetime.timedelta(minutes=3)
}

cities = '{{ var.json.getweatherCities }}'

dirname = Path(__file__).absolute().parent
with open(os.path.join(dirname, 'weatherdataschema.json'), "r", encoding="utf8") as f:
    weather_data_schema: str = json.loads(f.read())

with DAG(dag_id='open_weather_map_extraction',
         schedule_interval='00 3 * * *',
         default_args=default_dag_args,
         catchup=False,
         user_defined_macros={
             'env': os.environ,
             'exportTable': 'WEATHER_DATA',
             'exportDataset': 'EXTRACTION',
             'storesAndClustersTable': 'STORES_CLUSTERS',
        }) as dag:


    start = DummyOperator(
        task_id='start'
    )
    
    get_weather_from_api = PythonOperator(
                task_id="get_weather_from_api",
                python_callable=get_weather_data_from_api,
                op_args=[cities]
            )
    gcs_backup = PythonOperator(
                task_id="weather_data_from_api_backup",
                python_callable=upload_to_bucket,
                op_args=["ar-data-extraction-backup","dags/open-api-extract/weatherData.csv"]
            )


    load_gcs_to_bq = GCSToBigQueryOperator(
                        task_id='load_weather_data_gcs_to_bq',
                        bucket='ar-data-extraction-backup',
                        source_objects='dags/open-api-extract/weatherData.csv',
                        destination_project_dataset_table='{{ env["GCP_PROJECT"] }}.{{ exportDataset }}.{{ exportTable }}',
                        schema_fields=[weather_data_schema],
                        skip_leading_rows=1,
                        write_disposition="WRITE_APPEND",
                        field_delimiter=",",
                    )


    end = DummyOperator(
        task_id='end'
    )



start >> \
    get_weather_from_api >> \
    gcs_backup >> \
    load_gcs_to_bq >> \
    end
