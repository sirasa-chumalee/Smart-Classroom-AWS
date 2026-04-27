#mock data: GET/submissions
submissions = [
    #คะแนนปกติ confidence มากว่าที่กำหนด
    {
        "submissionId": "sub-123",
        "studentId": "6501001",
        "labId": "lab-01",
        "fileKey": "submissions/6501001/171000_lab1.jpg", #TA ดูรุปได้ มนจว่าต้องมีมั้ย
        "confidence": 91.5,
        "status": "accepted",
        "grade": None
    },
    #cheak กรณีค่า confidence ส่งมาน้อยกว่าที่กำหนด (90% ??) --> error TA ไม่ต้องให้คะแนน
    {
        "submissionId": "sub-124",
        "studentId": "6501002",
        "labId": "lab-01",
        "fileKey": "submissions/6501002/172000_lab1.jpg",
        "confidence": 75.0, 
        "status": "failed",
        "grade": None
    }
]

MIN_CONFIDENCE = 90

#FUNCTION หลัก
def grade_submission(submission_id, grade):
    #check TA กรอกคะแนนผิด
    if grade < 0 or grade > 100:
        return {"error": "Grade must be 0-100"}

    for i in submissions:
        if i["submissionId"] == submission_id:

            #check confidence
            if i["confidence"] < MIN_CONFIDENCE:
                return {"error": "This submission is not confident enough for TA grading"}

            #check status
            #accept --> ผ่าน
            #failed --> ไม่ผ่าน
            if i["status"] != "accepted":
                return {"error": "Submission is not ready for TA grading"}

            #ให้คะแนนแล้ว status เปลี่ยนจาก accepted --> graded
            i["grade"] = grade
            i["status"] = "graded"
            return i

    return {"error": "Submission not found"}

#-----test ลองกรอกคะแนนเอง----
print("\nAvailable submissions:")

for i in submissions:
    print("-", i["submissionId"], "| image:", i["fileKey"], "| status:",i["status"]) #งานนศทั้งหมด

sid = input("\nEnter submission ID: ")
grade = int(input("Enter grade (0-100): "))

result = grade_submission(sid, grade)

print("\n========== RESULT ==========")
if "error" in result:
    print("ERROR:", result["error"])
else:
    for key, value in result.items():
        print(f"{key}: {value}")