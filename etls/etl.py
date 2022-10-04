import click
import json
import pandas as pd
import logging
import boto3
from botocore.exceptions import ClientError
import os
import awswrangler as wr


def _read_data():
    data = ""
    f = open("./starlink_historical_data.json", "r")
    data = f.read()
    data = data.replace("\n","")
    data = data.replace(" ","")
    data = json.loads(data)
    df = pd.DataFrame(data)
    return df


def get_bucket_connection():
    s3_client = boto3.client('s3',aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    return s3_client

def _save_to_bucket(path, file_name):
    
    s3_client = get_bucket_connection()
    bucket = "starlink-test"
    try:
        s3_client.upload_file(path, bucket, "raw/"+file_name)
    except ClientError as e:
        logging.error(e)
        return False

def _save_local(path, str_to_save):
    file_object = open(path, 'w')
    file_object.write(str_to_save)
    file_object.close()
   

@click.command()
def start():
    df = _read_data()
    df_sorted = df.iloc[df['spaceTrack'].str.get('CREATION_DATE').astype(str).argsort()]
    data = df_sorted.to_dict('records')
    string_json = ""
    for item in data:
        string_json = string_json + str(json.dumps(item))+"\n"
    name_file = "historical.json"
    path = "./output/" + name_file 
    _save_local(path, string_json)
    _save_to_bucket(path, name_file)

start()