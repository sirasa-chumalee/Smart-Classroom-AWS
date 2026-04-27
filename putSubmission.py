import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
submission_table = dynamodb.Table("Submission")

def lambda_handler(event, context):
    try:
        submission_id = event["pathParameters"]["submissionId"]
        body = json.loads(event["body"])
        score = body.get("score")
        feedback = body.get("feedback", "")

        # ---------- Validate score ----------
        if score is None or score < 0 or score > 100:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Score must be between 0 and 100"
                })
            }

        # ---------- Load submission ----------
        submission_response = submission_table.get_item(
            Key={"submissionId": submission_id}
        )

        if "Item" not in submission_response:

            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Submission not found"
                })
            }

        submission = submission_response["Item"]