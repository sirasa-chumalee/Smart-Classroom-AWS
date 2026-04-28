const API_BASE = "https://3hx98cs12a.execute-api.us-east-1.amazonaws.com/dev";
const S3_BUCKET = "lab-st-pic";

const sleep = ms => Promise(r => setTimeout(r,ms));

function authHeaders() {
  const token = localStorage.getItem("lab_token") || "";
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  };
}

// GET /labs
async function apiGetLabs() {
    const res = await fetch(`${API_BASE}/labs`, {
        headers: authHeaders()
    });

    return res.json();
}

//POST /labs
async function apiCreateLab(payload) {
    const res = await fetch(`${API_BASE}/labs`,{
        method : "POST",
        headers: authHeaders(),
        body: JSON.stringify({
            title: payload.title,
            description: payload.description,
            keywords: payload.keywords
        })
    });
    return res.json();
}

//POST /labs/upload-example for TA
async function apiUploadLabExample(labId, fileName, fileType) {
    const res = await fetch(`${API_BASE}/labs/upload-example`, {
        method: "POST",
        headers : authHeaders(),
        body : JSON.stringify({
            labId,
            fileName,
            fileType
        })
    });

    return res.json();
}

// GET /submissions/studentId
async function apiGetStudentSubmissions(studentId) {
    const res = await fetch(`${API_BASE}/submissions?studentId=${studentId}`, {
        headers : authHeaders()
    });
    
    return res.json();
}

async function apiGetAllSubmissions() {
    const res = await fetch(`${API_BASE}/submissions`, {
        headers : authHeaders()
    });

    return res.json();
}

// PUT /submissions/{submissionId}
async function apiSaveGrade(submissionId, score, feedback) {
    const res = await fetch(`${API_BASE}/submissions/${submissionId}/grade`, {
        method : "PUT",
        headers : authHeaders(),
        body : JSON.stringify({score, feedback})
    });
    
    return res.json();
}

// POST /get-upload-url
async function apiGetPresignedUrl(labId, fileName, fileType) {
    const res = await fetch(`${API_BASE}/get-upload-url`, {
        method: "POST",
        headers : authHeaders(),
        body : JSON.stringify({
            labId,
            fileName,
            fileType
        })
    });
    
    return res.json();
}

async function apiUploadToS3(presignedUrl, file) {
    await fetch(presignedUrl, {
        method: "PUT",
        body: file
    });
}

// POST /submissions
async function apiCreateSubmission(studentId, labId, fileKey) {
    const res = await fetch(`${API_BASE}/submissions`, {
        method: "POST",
        headers: authHeaders(),
        body:JSON.stringify({
            fileKey,
            studentId,
            labId
        })
    });

    return res.json();
}