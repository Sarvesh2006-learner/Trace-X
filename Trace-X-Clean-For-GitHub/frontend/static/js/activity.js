const pageSize = 100;
let offset = 0;

async function loadActivity() {
  const status = document.getElementById("activity-status");
  const response = await fetch(`/api/admin/activity?limit=${pageSize}&offset=${offset}`, { credentials: "include" });
  const data = await response.json();
  if (response.status === 401) return location.href = "/login.html";
  if (response.status === 403) return location.href = "/dashboard.html";
  if (!response.ok) {
    status.textContent = data.error || "Could not load activity.";
    return;
  }

  status.textContent = `${data.total} recorded activities`;
  const container = document.getElementById("activity-table");
  container.replaceChildren();
  if (!data.activities.length) {
    container.textContent = "No activities have been recorded yet.";
  } else {
    const table = document.createElement("table");
    const headings = ["Date and time (UTC)", "User", "Activity", "Details"];
    const header = table.createTHead().insertRow();
    headings.forEach(text => {
      const cell = document.createElement("th");
      cell.textContent = text;
      header.appendChild(cell);
    });
    const body = table.createTBody();
    data.activities.forEach(activity => {
      const row = body.insertRow();
      const values = [
        new Date(activity.created_at).toLocaleString(undefined, { timeZone: "UTC" }),
        activity.username,
        activity.action.replaceAll("_", " "),
        activity.details || ""
      ];
      values.forEach(value => {
        const cell = row.insertCell();
        cell.textContent = value;
      });
    });
    container.appendChild(table);
  }

  document.getElementById("previous").disabled = offset === 0;
  document.getElementById("next").disabled = offset + pageSize >= data.total;
  document.getElementById("page-label").textContent =
    data.total ? `${offset + 1}-${Math.min(offset + pageSize, data.total)} of ${data.total}` : "0 activities";
}

function changePage(direction) {
  offset = Math.max(0, offset + direction * pageSize);
  loadActivity();
}

async function logout() {
  await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
  location.href = "/login.html";
}

loadActivity();
