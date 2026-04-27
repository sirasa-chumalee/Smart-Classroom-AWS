import boto3
import json

MY_ACCESS_KEY = "XXX"
MY_SECRET_KEY = "XXX"
MY_SESSION_TOKEN = "XXX"
rekognition_client = boto3.client(
    'rekognition', 
    region_name='us-east-1',
    aws_access_key_id=MY_ACCESS_KEY,
    aws_secret_access_key=MY_SECRET_KEY,
    aws_session_token=MY_SESSION_TOKEN
)

textract_client = boto3.client(
    'textract', 
    region_name='us-east-1',
    aws_access_key_id=MY_ACCESS_KEY,
    aws_secret_access_key=MY_SECRET_KEY,
    aws_session_token=MY_SESSION_TOKEN
)

TARGET_KEYWORDS = {"enabled", "30days"}

#Clean input text
def normalize(text):
    return text.lower().replace(" ", "")

#เช็ค text กับ keyword
def find_keywords(text_items):
    found = {}

    for text, confidence in text_items:
        normalized = normalize(text)

        for kw in TARGET_KEYWORDS:
            if kw in normalized:
                found[kw] = max(found.get(kw, 0), confidence)

    return found


def run_rekognition(image_bytes):
    response = rekognition_client.detect_text(Image={"Bytes": image_bytes})

    #เอาทั้ง text กับ confidence
    text_items = [
        (t["DetectedText"], t["Confidence"])
        for t in response.get("TextDetections", [])
    ]

    return find_keywords(text_items)


def run_textract(image_bytes):
    response = textract_client.detect_document_text(Document={"Bytes": image_bytes})

    text_items = [
        (block["Text"], block["Confidence"])
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]

    return find_keywords(text_items)


def lambda_handler(event, context):

    #ใส่รูป
    image_filename = "image.png"

    with open(image_filename, "rb") as f:
        image_bytes = f.read()

    print(f"Validating image: {image_filename}")

    # Tier 1: Rekognition
    try:
        print("Tier 1: Rekognition")
        found = run_rekognition(image_bytes)

        #ต้องเจอ Keyword ครบทุกคำถึงจะ Pass
        if TARGET_KEYWORDS.issubset(found.keys()):
            print("Pass: Rekognition found all required keywords.")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "Pass",
                    "engine": "Rekognition",
                    "keywords": found
                })
            }

    except Exception as e:
        print(f"Rekognition Error: {str(e)}. Proceeding to fallback.")

    print("Rekognition fallback triggered. Executing Tier 2: Amazon Textract...")

    # Tier 2: Textract
    try:
        print("Tier 2: Textract")
        found = run_textract(image_bytes)

        if TARGET_KEYWORDS.issubset(found.keys()):
            print("Pass: Textract found all required keywords.")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "Pass",
                    "engine": "Textract",
                    "keywords": found
                })
            }

        missing = list(TARGET_KEYWORDS - set(found.keys()))
        print(f"Reject: Missing keywords: {missing}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "Reject",
                "missing": missing,
                "detected_keywords": found
            })
        }

    except Exception as e:
        print("Textract error:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"status": "Error"})
        }


if __name__ == "__main__":
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=4))
