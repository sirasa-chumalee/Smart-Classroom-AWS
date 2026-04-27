import boto3
import json
import os

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def lambda_handler(event, context):

    print("Received GET request for submissions dashboard.")

    table_name = os.environ.get('TABLE_NAME', 'Submission')

    table = dynamodb.Table(table_name)

    try:

        response = table.scan()

        items = response.get('Items', [])

        formatted_submissions = []

        for item in items:

            formatted_submissions.append({

                "submissionId": item.get("submissionId"),

                "labId": item.get("labId"),

                "studentId": item.get("studentId"),

                "submittedAt": item.get("submittedAt"),

                "score": float(item.get("score", 0)),

                "avgConfidence": float(
                    item.get("avgConfidence", 0)
                ),

                "engine": item.get("engine", "pending"),

                "keywordsDetected": item.get(
                    "keywordsDetected", []
                ),

                "missingWords": item.get(
                    "missingWords", []
                ),

                "status": item.get("status", "pending")
                "fileKey": item.get("fileKey")
            })


        print(
            f"Successfully retrieved {len(formatted_submissions)} submissions."
        )


        return {

            "statusCode": 200,

            "headers": {

                "Access-Control-Allow-Origin": "*",

                "Access-Control-Allow-Credentials": True,

                "Content-Type": "application/json"

            },

            "body": json.dumps(formatted_submissions)

        }


    except Exception as e:

        print(f"Database Error: {str(e)}")

        return {

            "statusCode": 500,

            "headers": {

                "Access-Control-Allow-Origin": "*"

            },

            "body": json.dumps({

                "error": "Internal Server Error while fetching data"

            })

        }
