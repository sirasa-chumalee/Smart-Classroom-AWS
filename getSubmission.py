import boto3
import json
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    print("Received GET request for submissions dashboard.")

    table_name = os.environ.get('TABLE_NAME', 'your-dynamodb-table-name')
    table = dynamodb.Table(table_name)

    try:
        response = table.scan()
        items = response.get('Items', [])

        formatted_submissions = []
        for item in items:
            formatted_submissions.append({
                "submissionId": item.get("submissionId", "unknown"),
                "avg_confidence": float(item.get("avg_confidence", 0.0)),
                "engine": item.get("engine", "N/A"),
                "keywordDetected": list(item.get("keywordDetected", [])),
                "status": item.get("status", "pending"),
                "missing_words": list(item.get("missing_words", []))
            })

        print(f"Successfully retrieved {len(formatted_submissions)} submissions.")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(formatted_submissions)
        }

    except Exception as e:
        print(f"Database Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal Server Error while fetching data'})
        }

if __name__ == "__main__":
    class MockContext:
        def __init__(self):
            self.aws_request_id = "local-test-id-12345"

    mock_event = {}
    mock_context = MockContext()

    os.environ['TABLE_NAME'] = 'your-dynamodb-table-name'

    print("Running Lambda locally...")
    result = lambda_handler(mock_event, mock_context)

    print("\nResponse:")
    print(json.dumps(result, indent=2))
