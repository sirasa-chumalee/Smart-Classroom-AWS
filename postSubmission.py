import boto3
import json
from botocore.client import Config
from datetime import datetime
import os

s3 = boto3.client(
    "s3",
    config=Config(signature_version="s3v4")
)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

BUCKET_NAME = "lab-st-pic"
TABLE_NAME = os.environ.get("TABLE_NAME", "Submission")


def lambda_handler(event, context):

    body = json.loads(event["body"])

    filename = body["fileName"]
    file_type = body["fileType"]
    lab_id = body["labId"]

    # fallback static student for now
    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
    student_id = claims["preferred_username"]

    submission_id = "sub-" + context.aws_request_id[:8]

    file_key = f"labs/{lab_id}/submissions/{submission_id}/{filename}"

    upload_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key,
            "ContentType": file_type
        },
        ExpiresIn=300
    )

    table = dynamodb.Table(TABLE_NAME)

    table.put_item(
        Item={
            "submissionId": submission_id,
            "labId": lab_id,
            "studentId": student_id,
            "submittedAt": datetime.utcnow().isoformat(),
            "score": 0,
            "avgConfidence": 0,
            "engine": "pending",
            "keywordsDetected": [],
            "missingWords": [],
            "status": "pending",
            "fileKey": file_key
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "uploadUrl": upload_url,
            "fileKey": file_key,
            "submissionId": submission_id
        })
    }
