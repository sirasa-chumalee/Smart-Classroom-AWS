import boto3
import json
import uuid
import os
from botocore.client import Config


BUCKET_NAME = os.environ.get("BUCKET_NAME", "lab-st-pic")

s3 = boto3.client(
    "s3",
    config=Config(signature_version="s3v4")
)

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
            "Key": file_key,
            "ContentType": file_type 
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


if __name__ == "__main__":
    class MockContext:
        def __init__(self):
            
            self.aws_request_id = str(uuid.uuid4())

    mock_event = {
        "body": json.dumps({
            "fileName": "test_assignment.pdf",
            "fileType": "application/pdf",
            "labId": "cs-102"
        })
    }
    mock_context = MockContext()

    response = lambda_handler(mock_event, mock_context)

    print("\n Response:")
    print(json.dumps(response, indent=2))
