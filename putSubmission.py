import json

def lambda_handler(event, context):
    body = json.loads(event["body"])
    score = body.get("score")

    if score is None or score < 0 or score > 100:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Score must be between 0 and 100"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Valid input"})
    }