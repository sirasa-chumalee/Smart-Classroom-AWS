let currentUser  = null;
let activeLab    = null;
let selectedFile = null;

let allLabs = [];
let allSubs = [];

// Init
async function init() {
  const stored = localStorage.getItem("lab_user");

    if (!stored) {
    // Fallback: auto-login as demo student so page always works
    currentUser = { userId: "student01", role: "student", name: "Student Demo", email: "student01@tu.ac.th" };
    } else {
    currentUser = JSON.parse(stored);
    if (currentUser.role !== "student") {
        window.location.href = "dashboard.html"; return;
    }
    }

  document.getElementById("u-avatar").textContent =
    currentUser.userId.slice(-2).toUpperCase();
  document.getElementById("u-name").textContent  = currentUser.name;
  document.getElementById("u-email").textContent = currentUser.email;
  document.getElementById("pg-stid").textContent = currentUser.userId;

  await loadDashboard();
}

async function loadDashboard() {
    try {
        allLabs = await apiGetLabs();

        try {
            allSubs = await apiGetStudentSubmissions(currentUser.userId);
        } catch (e) {
            console.warn("Submissions failed, continuing...");
            allSubs = [];
        }

        renderLabGrid();
        renderGradesTable();

    } catch (e) {
        console.error(e);
        toast("Failed to load");
    }
}

function renderLabGrid() {
    console.log("Labs : ", allLabs);
    const grid = document.getElementById("lab-grid");

    if (!allLabs || !allLabs.length) {
        grid.innerHTML = "<p>No labs available</p>";
        return;
    }

    grid.innerHTML = allLabs.map(lab => {
        const sub = (allSubs || []).find(s => s.labId === lab.labId);

        const status = sub ? sub.status : "none";
        const label = sub ? cap(sub.status) : "Not submitted";

        return `
        <div class="lab-card" onclick="openSubmitModal('${lab.labId}')">
            <div><span class="badge badge-${status}">${label}</span></div>
            <div class="lc-name">${lab.title}</div>
            <div class="lc-desc">${lab.description}</div>
        </div>
        `;
    }).join("");
}

function renderGradesTable() {
    const tb = document.getElementById("grades-tbody");
    if (!allSubs.length) {
        tb.innerHTML = '<tr><td colspan="5">No Submissions yet</td></tr>';
        return;
    }

    tb.innerHTML = allSubs.map(s => {
        const lab = allLabs.find(l => l.labId === s.labId);

    return `
      <tr>
        <td><b>${lab ? lab.title : s.labId}</b></td>
        <td>${s.submittedAt || "-"}</td>
        <td><span class="badge badge-${s.status}">${cap(s.status)}</span></td>
        <td>${s.score != null ? s.score + " / 100" : "–"}</td>
        <td>${s.feedback || "–"}</td>
      </tr>
        `;
    }).join("");
}

function showTab(name, btn) {
    document.getElementById("tab-dashboard").style.display = name === "dashboard" ? "" : "none";
    document.getElementById("tab-grades").style.display    = name === "grades"    ? "" : "none";
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
}

function openSubmitModal(labId) {
    activeLab = allLabs.find(l => l.labId === labId);
    if (!activeLab) return;

    document.getElementById("submit-lab-title").textContent = activeLab.title;
    document.getElementById("submit-lab-name").textContent = activeLab.title;
    document.getElementById("submit-desc").textContent = activeLab.description;

    document.getElementById("dropzone").style.display = "flex";
    document.getElementById("file-chip").innerHTML = "";
    document.getElementById("result-area").innerHTML = "";

    document.getElementById("btn-submit").disabled = true;
    document.getElementById("btn-submit").textContent = "Submit";

    selectedFile = null;
    document.getElementById("backdrop-submit").classList.add("open");
}

function closeSubmitModal() {
    document.getElementById("backdrop-submit").classList.remove("open");
}

document.getElementById("backdrop-submit").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeSubmitModal();
});

function onDrop(e) {
    e.preventDefault();
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
}

function onFileInput(e) {
    if (e.target.files[0]) setFile(e.target.files[0]);
}

function setFile(f) {
if (!["image/png", "image/jpeg"].includes(f.type)) {
    toast("PNG / JPEG only");
    return;
  }

  selectedFile = f;

  document.getElementById("dropzone").style.display = "none";

  document.getElementById("file-chip").innerHTML = `
    <div class="file-chip">
      <span>🖼</span>
      <span>${f.name}</span>
      <span class="chip-rm" onclick="removeFile()">✕</span>
    </div>
  `;

  document.getElementById("btn-submit").disabled = false;
}

function removeFile() {
    selectedFile = null;
    document.getElementById("file-inp").value = "";
    document.getElementById("file-chip").innerHTML = "";
    document.getElementById("dropzone").style.display = "flex";
    document.getElementById("btn-submit").disabled = true;
}

async function doSubmit() {
    if (!selectedFile || !activeLab) return;

    const btn = document.getElementById("btn-submit");
    btn.disabled = true;
    btn.textContent = "Uploading...";

    try {
        const { uploadUrl, fileKey } = await apiGetPresignedUrl(
        activeLab.labId,
        selectedFile.name,
        selectedFile.type,
        currentUser.userId
        );
        
        btn.textContent = "Processing...";

        await apiUploadToS3(uploadUrl, selectedFile);
        console.log("yay yay", uploadUrl, fileKey);
        // const result = await apiCreateSubmission(
        // currentUser.userId,
        // activeLab.labId,
        // fileKey
        // );

        // const isPass = result.status === "accepted";

        // document.getElementById("result-area").innerHTML = `
        // <div class="result-msg ${isPass ? "result-pass" : "result-fail"}">
        //     ${isPass ? "✅ Accepted" : "❌ Rejected"} (${result.engine}) —
        //     Confidence: ${result.avg_confidence}%
        // </div>
        // `;

        await loadDashboard();

        toast("Submitted ✅");

    } catch (e) {
        console.error(e);
        toast("Upload failed ❌");
    }

    btn.textContent = "Submit";
    btn.disabled = false;
}

// Helpers
function logout() {
  localStorage.removeItem("lab_user");
  window.location.href = "login.html";
}

function cap(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3000);
}

init();