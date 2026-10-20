async function loadRecentActivity() {
  const section = document.getElementById("recent-activity-section");
  const status = document.getElementById("recent-activity-status");
  const list = document.getElementById("recent-activity-list");
  section.hidden = false;

  try {
    const response = await fetch("/api/admin/activity?limit=5&offset=0", { credentials: "include" });
    const data = await response.json();
    if (!response.ok) {
      status.textContent = data.error || "Could not load recent activity.";
      return;
    }

    status.textContent = data.total ? "Latest recorded actions" : "No activities have been recorded yet.";
    data.activities.forEach(activity => {
      const item = document.createElement("article");
      item.className = "activity-item";

      const heading = document.createElement("div");
      heading.className = "activity-heading";
      const action = document.createElement("strong");
      action.textContent = activity.action.replaceAll("_", " ");
      const timestamp = document.createElement("time");
      timestamp.dateTime = activity.created_at;
      timestamp.textContent = new Date(activity.created_at).toLocaleString();
      heading.append(action, timestamp);

      const user = document.createElement("p");
      user.className = "activity-user";
      user.textContent = `User: ${activity.username}`;
      item.append(heading, user);

      if (activity.details) {
        const details = document.createElement("p");
        details.textContent = activity.details;
        item.appendChild(details);
      }
      list.appendChild(item);
    });
  } catch {
    status.textContent = "Could not load recent activity. Please refresh the page to try again.";
  }
}

async function load() {
  const me = await fetch("/api/auth/me", { credentials: "include" }).then(response => response.json());
  if (!me.authenticated) return location.href = "/login.html";

  welcome.textContent = `Signed in as ${me.username} (${me.role})`;
  document.getElementById("activity-link").hidden = me.role !== "admin";
  if (me.role === "admin") loadRecentActivity();

  const data = await fetch("/api/evidence", { credentials: "include" }).then(response => response.json());
  const highRisk = data.filter(item => item.analysis &&
    (item.analysis.duplicate_found || item.analysis.content_match_found));
  const mediumRisk = data.filter(item => {
    const analysis = item.analysis;
    return analysis && !analysis.duplicate_found && !analysis.content_match_found &&
      (analysis.semantic_score != null || analysis.image_similarity != null ||
        analysis.morphing_indicator === "ELEVATED_RECOMPRESSION_DIFFERENCE" ||
        analysis.morphing_indicator === "MODERATE_RECOMPRESSION_DIFFERENCE");
  });
  const suspiciousCount = highRisk.length + mediumRisk.length;

  document.getElementById("total").textContent = data.length;
  document.getElementById("suspicious").textContent = suspiciousCount;
  document.getElementById("high").textContent = highRisk.length;
  document.getElementById("medium").textContent = mediumRisk.length;
  document.getElementById("low").textContent = data.length - suspiciousCount;
  table.innerHTML = `<table><tr><th>ID</th><th>Case</th><th>File</th><th>SHA-256</th><th>Status</th><th></th></tr>${data.map(item =>
    `<tr><td>${item.id}</td><td>${item.case_id}</td><td>${item.filename}</td><td class="hash">${item.sha256}</td><td>${item.analysis?.duplicate_found ? '<span class="bad">DUPLICATE</span>' : item.analysis?.content_match_found ? '<span class="warn">CONTENT MATCH</span>' : '<span class="ok">NO MATCH</span>'}</td><td><a href="/result.html?id=${item.id}">View</a></td></tr>`
  ).join("")}</table>`;
}

async function logout() {
  await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
  location.href = "/login.html";
}

load();