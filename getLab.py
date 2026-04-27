import json
import boto3

dynamodb = boto3.resource("dynamodb")

LAB_TABLE = "Lab"
table = dynamodb.Table(LAB_TABLE)


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        labs = []

        db_response = table.scan()

        for item in db_response.get("Items", []):
            labs.append({
                "labId": item.get("labId"),
                "title": item.get("title")
            })

        return response(200, labs)

    except Exception as e:
        print("Error:", str(e))
        return response(500, {"error": "Failed to fetch labs"})
