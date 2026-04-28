import boto3
import json

BUCKET_NAME = "lab-st-pic"

s3 = boto3.client("s3")

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}

    file_key = params.get("key")

    if not file_key:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Missing file key"
            })
        }

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key
        },
        ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "url": url
        })
    }