const $ = (id) => document.getElementById(id);

function setStatus(text, cls = "") {
  $("status").className = cls;
  $("status").textContent = text;
}

async function loadLinks() {
  const res = await fetch("/api/links");
  const data = await res.json();
  if (!res.ok) {
    setStatus("Error: " + data.detail, "error");
    $("open").disabled = true;
    return;
  }
  $("count").textContent = data.count;
  $("links").innerHTML = "";
  for (const link of data.links) {
    const li = document.createElement("li");
    li.textContent = link;
    $("links").appendChild(li);
  }
  $("open").disabled = data.count === 0;
}

async function openLinks() {
  $("open").disabled = true;
  setStatus("Opening Chrome...");
  try {
    const res = await fetch("/api/open", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    setStatus(`Opened ${data.tabs_opened} tab(s) in ${data.profile}.`, "ok");
  } catch (e) {
    setStatus("Error: " + e.message, "error");
  } finally {
    $("open").disabled = false;
  }
}

$("open").addEventListener("click", openLinks);
$("reload").addEventListener("click", () => { setStatus(""); loadLinks(); });
loadLinks();
