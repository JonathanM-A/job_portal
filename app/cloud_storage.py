from google.cloud import storage
from datetime import timedelta

client = storage.Client()

def upload_to_gcs(file, destination_file_name, bucket_name):
    """Uploads a file to Google Cloud Storage"""
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_file_name)

        blob.upload_from_file(file)
        url = blob.generate_signed_url(expiration=timedelta(days=30), method="GET")
        # url = blob.public_url
        return url
    except Exception as e:
        print (f"Error occured during upload: {e}")
        return None


def dowload_from_gcs(bucket_name, source_file_name, save_file_as):
    """Downloads a file from Google Cloud Storage"""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_file_name)
    blob.download_to_file_name(save_file_as)
