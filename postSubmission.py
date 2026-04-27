import boto3
import json
from botocore.client import Config


s3 = boto3.client(
    "s3",
    config=Config(signature_version="s3v4")
)


BUCKET_NAME = "lab-st-pic"


def lambda_handler(event, context):
    body = json.loads(event["body"])


    filename = body["fileName"]
    file_type = body["fileType"]
    lab_id = body["labId"]


    submission_id = "sub-" + context.aws_request_id[:8]
    file_key = f"labs/{lab_id}/submissions/{submission_id}/{filename}"


    upload_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key
        },
        ExpiresIn=300
    )


    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "uploadUrl": upload_url,
            "fileKey": file_key,
            "submissionId": submission_id
        })
    }

