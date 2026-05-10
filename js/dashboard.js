let allLabs = [];
let allSubs = [];

let currentTA = null;
let editingSubId = null;

async function init() {
    const stored = localStorage.getItem("lab_user");

    if (!stored) {
    // Fallback demo TA
    currentTA = { userId: "ta01", role: "ta", name: "TA Demo", email: "ta01@tu.ac.th" };
    } else {
    currentTA = JSON.parse(stored);
    if (currentTA.role !== "ta") {
        window.location.href = "student.html"; return;
    }
    }

    document.getElementById("ta-lbl").textContent = currentTA.userId;

    allLabs = await apiGetLabs();
    allSubs = await apiGetAllSubmissions();
    
    populateLabFilter();
    renderTable(allSubs);
}

function renderTable(subs) {
    const tb = document.getElementById("sub-tbody");
    if(!subs.length) {
        tb.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:36px;font-family:var(--mono);font-size:12px;color:var(--muted);">No submissions found</td></tr>`;
        return;
    }
    tb.innerHTML = subs.map(s => {
        const lab = allLabs.find(l => l.labId === s.labId);
        const labTitle = lab ? lab.title : s.labId;

    return `
      <tr>
        <td><b>${labTitle}</b></td>
        <td>${s.studentId}</td>
        <td>${s.submittedAt || "-"}</td>
        <td><span class="badge badge-${s.status}">${cap(s.status)}</span></td>
        <td>${s.score ?? "-"}</td>
        <td>${s.avgConfidence ?? "-"}%</td>
        
        <td>
            ${renderMissingKeywordPreview(s.missingWords)}
        </td>

        <td>
          <button onclick="openEditModal('${s.submissionId}')">Edit</button>
        </td>
      </tr>
    `;
    }).join("");
}

function applyFilter() {
    const lab = document.getElementById("f-lab").value;
    const status = document.getElementById("f-status").value.toLowerCase();
    const search = document.getElementById("f-search").value.trim();
    let data = [...allSubs];
    if (lab)    data = data.filter(s => s.labId === lab);
    if (status) data = data.filter(s => s.status === status);
    if (search) data = data.filter(s => s.studentId.includes(search));
    renderTable(data);
}

async function openEditModal(subId) {
    const s = allSubs.find(x => x.submissionId === subId);
    if (!s) return;

    editingSubId = subId;

    const lab = allLabs.find(l => l.labId === s.labId);

    document.getElementById("edit-title").textContent =
        lab ? lab.title : s.labId;

    document.getElementById("edit-score").value =
        s.score ?? "";

    document.getElementById("edit-feedback").value =
        s.feedback || "";

    const badge = document.getElementById("edit-badge");
    badge.className = "badge badge-" + s.status;
    badge.textContent = cap(s.status);

    // LOAD SUBMISSION IMAGE
    if (s.fileKey) {
        try {
            const imageUrl = await apiGetSubmissionImage(s.fileKey);

            document.getElementById("edit-attachments").innerHTML = `
                <img src="${imageUrl}"
                      style="max-width:100%;
                             border-radius:8px; cursor:pointer;"
                      onclick="enlargeImage(this.src)">`;

        } catch (err) {
            console.error("Image load failed:", err);
            
            if (err?.response) {
                console.log("Response:", err.response);
            }

            toast(err.message || "Image load failed");

            document.getElementById("edit-attachments").innerHTML = "Unable to load attachment.";
        }
    } else {
        document.getElementById("edit-attachments").innerHTML = "No attachment.";
    }
    renderMissingKeywords(s.missingWords);
    openBackdrop("backdrop-edit");
}

async function saveGrade() {
    const score = parseInt(document.getElementById("edit-score").value);
    const feedback = document.getElementById("edit-feedback").value;

    const btn = document.getElementById("btn-save-grade");
    btn.textContent = "Saving...";
    btn.disabled = true;
    try {
        await apiSaveGrade(editingSubId, score, feedback);

        allSubs = await apiGetAllSubmissions();
        renderTable(allSubs);

        closeBackdrop("backdrop-edit");
        toast("Saved");
    } catch (e) {
        toast("Error saving");
    }

    btn.textContent = "Save";
    btn.disabled = false;
}

function openCreateModal() {
    resetCreateModal();
    
    document.getElementById("create-title").textContent =
        "Lab " + (allLabs.length + 1);
    openBackdrop("backdrop-create");
}
// Show/hide datetime input
document.addEventListener("change", e => {
    if (e.target.name === "due")
    document.getElementById("new-due").style.display = e.target.value === "date" ? "block" : "none";
});

function setCreateFile(f) {
  if (!f) return;

  document.getElementById("create-dropzone").style.display = "none";

  document.getElementById("create-file-chip").innerHTML = `
    <div class="file-chip">
            <span>${f.type.includes("pdf") ? "📄" : "🖼"}</span>
            <span>${escapeHtml(f.name)}</span>
            <span class="chip-rm" onclick="clearCreateFile()">✕</span>
        </div>
    `;
    const previewArea = document.getElementById("create-preview-area");

    // IMAGE PREVIEW
    if (f.type.startsWith("image/")) {

        const url = URL.createObjectURL(f);

        previewArea.innerHTML = `
            <img src="${url}"
                 onclick="enlargeImage(this.src)"
                 style="
                    max-width:200px;
                    margin-top:12px;
                    border-radius:10px;
                    cursor:pointer;
                    border:1px solid var(--border);
                 ">
        `;

    }

    // PDF PREVIEW
    else if (f.type === "application/pdf") {

        previewArea.innerHTML = `
            <div class="pdf-preview">
                📄 PDF selected
            </div>
        `;
    }

    else {
        previewArea.innerHTML = "";
    }
}

function clearCreateFile() {
    document.getElementById("create-file-inp").value = "";
    document.getElementById("create-file-chip").innerHTML = "";
        document.getElementById("create-preview-area").innerHTML = "";
    document.getElementById("create-dropzone").style.display = "block";
}

async function postLab() {
    const desc = document.getElementById("new-desc").value.trim();
    const kwRaw = document.getElementById("new-keywords").value.trim();
    
    if (!desc) {
        toast("Description required");
        return;
    }

    const keywords = kwRaw
        ? kwRaw.split(",").map(k => k.trim().toLowerCase()).filter(Boolean) : [];

    const title = "Lab " + (allLabs.length +1);

    const btn = document.getElementById("btn-post-lab");
    btn.textContent = "Posting...";
    btn.disabled = true;

    try {
        await apiCreateLab({
            title,
            description : desc,
            keywords
        });

        allLabs = await apiGetLabs();
        populateLabFilter();

        closeBackdrop("backdrop-create");
        toast("Lab created");
    } catch (e) {
        console.error(e);
        toast("Error creating lab");
    }

    btn.textContent = "Post";
    btn.disabled = false;
}

function populateLabFilter() {
    const select = document.getElementById("f-lab");

    select.innerHTML = `<option value="">Choose Lab</option>` +
        allLabs.map(l => `<option value="${l.labId}">${l.title}</option>`).join("");
}
function resetCreateModal() {
    document.getElementById("new-desc").value = "";
    document.getElementById("new-keywords").value = "";

    document.getElementById("create-file-inp").value = "";
    document.getElementById("create-file-chip").innerHTML = "";
    document.getElementById("create-preview-area").innerHTML = "";

    document.getElementById("create-dropzone").style.display = "flex";

    document.getElementById("new-points").value = 100;

    document.querySelector('input[name="grading"][value="points"]').checked = true;
    document.querySelector('input[name="due"][value="none"]').checked = true;

    document.getElementById("new-due").value = "";
    document.getElementById("new-due").style.display = "none";

    const btn = document.getElementById("btn-post-lab");
    btn.disabled = false;
    btn.textContent = "Post";
}

function resetEditModal() {
    editingSubId = null;

    document.getElementById("edit-title").textContent = "";

    document.getElementById("edit-score").value = "";
    document.getElementById("edit-feedback").value = "";

    document.getElementById("edit-badge").className = "badge";
    document.getElementById("edit-badge").textContent = "";

    document.getElementById("edit-attachments").innerHTML = "";
    document.getElementById("missing-keywords").innerHTML = "";

    const btn = document.getElementById("btn-save-grade");
    btn.disabled = false;
    btn.textContent = "Save";
}

// Helpers
function openBackdrop(id) {
    document.getElementById(id).classList.add("open");
}

function closeBackdrop(id) {

    if (id === "backdrop-create") {
        resetCreateModal();
    }

    if (id === "backdrop-edit") {
        resetEditModal();
    }

    document.getElementById(id).classList.remove("open");
}

function logout() {
    localStorage.removeItem("lab_user");
    window.location.href = "login.html";
}

function cap(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}

function renderMissingKeywords(words = []) {
    const box = document.getElementById("missing-keywords");
    const cleanWords = words.filter(Boolean);

    if (!cleanWords.length) {
        box.innerHTML = `<span class="keyword-empty">None</span>`;
        return;
    }

    box.innerHTML = cleanWords
        .map(word => `<span class="keyword-chip">${escapeHtml(word)}</span>`)
        .join("");
}

function renderMissingKeywordPreview(words = []) {

    const cleanWords = words.filter(Boolean);

    if (!cleanWords.length) {
        return `<span class="keyword-empty">None</span>`;
    }

    const visible = cleanWords.slice(0, 3);

    const chips = visible
        .map(word =>
            `<span class="keyword-chip">${escapeHtml(word)}</span>`
        )
        .join(" ");

    const extra =
        cleanWords.length > 3
            ? ` <span class="keyword-more">+${cleanWords.length - 3}</span>`
            : "";

    return chips + extra;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
function toast(msg) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 3000);
}

// Enlarge image functions
function enlargeImage(src) {
  document.getElementById('enlarge-img').src = src;
  document.getElementById('backdrop-enlarge').classList.add('open');
}

function closeEnlargeModal() {
  document.getElementById('backdrop-enlarge').classList.remove('open');
}

document.getElementById('backdrop-enlarge').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeEnlargeModal();
});

init();