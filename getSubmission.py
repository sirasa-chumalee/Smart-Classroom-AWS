import boto3
import json
import os
from decimal import Decimal

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
                "submissionId": item.get("submissionId", "unknown"),
                "avgConfidence": float(item.get("avgConfidence", 0.0)),
                "engine": item.get("engine", "N/A"),
                "keywordsDetected": item.get("keywordsDetected", []),
                "status": item.get("status", "pending"),
                "missingWords": item.get("missingWords", [])
            })

        print(f"Successfully retrieved {len(formatted_submissions)} submissions.")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '', 
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json'
            },
            'body': json.dumps(formatted_submissions)
        }

    except Exception as e:
        print(f"Database Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': ''
            },
            'body': json.dumps({'error': 'Internal Server Error while fetching data'})
        }
