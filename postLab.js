const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");


const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);


const TABLE_NAME = "Lab";
const MIN_CONFIDENCE = 50;

exports.handler = async (event) => {
    try {
        //รับ Input (API --> object)
        const body = typeof event.body === "string"
            ? JSON.parse(event.body)
            : event.body;

        //ดึงค่าจาก request
        const { title, description, keywords } = body || {};

        //ไม่มี title & keywords --> ERROR
        if (!title || !Array.isArray(keywords) || keywords.length === 0) {
            return response(400, { error: "Invalid input" });
        }

        //สร้าง labId
        const labId = `lab-${Date.now()}`; //timestamp เช่น lab-1711283748123

        //สร้าง object เก็บข้อมูลลง DB
        const item = {
            labId,
            title,
            description: description || "",
            keywords,
            minConfidence: MIN_CONFIDENCE,
            exampleImages: [], //เก็บรูปตัวอย่างที่ TA ส่งมา
            createdAt: new Date().toISOString() //timestamp
        };

        await dynamo.send(new PutCommand({
            TableName: TABLE_NAME,
            Item: item
        }));


        //ส่ง response กลับ
        return response(200, {
            message: "Lab created successfully",
            data: {
                labId: labId
            }
        });

        //กรณี ERROR
    } catch (err) {
        console.error(err);
        return response(500, { error: "Create lab failed" });
    }
};

//สร้าง response ให้ format เหมือนกันทุกครั้ง
//มี CORS → frontend เรียกได้
function response(statusCode, body) {
    return {
        statusCode,
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
        body: JSON.stringify(body)
    };
}