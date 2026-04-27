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