import logging
import os
import boto3


logger = logging.getLogger(__name__)
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET")
S3_LOCATION = os.environ.get("S3_LOCATION")


def connect_to_s3():
    s3 = boto3.client("s3")
    config = {
        "S3_KEY": S3_KEY,
        "S3_SECRET": S3_SECRET,
        "S3_BUCKET": S3_BUCKET,
        "S3_LOCATION": S3_LOCATION,
    }
    s3 = boto3.client(
        "s3",
        aws_access_key_id=config["S3_KEY"],
        aws_secret_access_key=config["S3_SECRET"],
    )
    return s3


def upload_to_s3(file_name):
    s3_client = connect_to_s3()
    try:
        s3_client.upload_file(file_name, "ankigen", f"{file_name}")
        logger.info(f"File {file_name} uploaded to S3")
    except Exception as e:
        logger.error(f"Error uploading file {file_name} to S3: {e}")
    return None


def generate_donload_link(file_name):
    s3_client = connect_to_s3()
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": file_name},
        ExpiresIn=3600,
    )
    return url
