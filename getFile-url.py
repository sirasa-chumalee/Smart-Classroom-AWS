import boto3
import json

BUCKET_NAME = "lab-st-pic"

s3 = boto3.client("s3")

def get_presigned_url(file_key):
    if not file_key:
        return {"error": "Missing file key"}
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key
        },
        ExpiresIn=300
    )
    return {"url": url}

#local test
if __name__ == "__main__":
    print("=== Local Test: Generate Presigned URL ===")
    file_key = input("Enter fileKey: ")
    result = get_presigned_url(file_key)
    print("\nResult:")
    print(json.dumps(result, indent=2))