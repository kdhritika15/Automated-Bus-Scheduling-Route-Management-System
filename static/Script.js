const searchBtn = document.getElementById("searchBtn");
const sourceInput = document.getElementById("source");
const destinationInput = document.getElementById("destination");
const busResult = document.getElementById("bus-result");
const routeMapFrame = document.getElementById("routeMapFrame");

// Tracks whether the current browser session is logged in as admin.
// Set by checkAuthStatus() on load and by the login/logout handlers.
let isAdmin = false;

const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const loginFormSection = document.getElementById("loginForm");
const adminSection = document.getElementById("admin");
const loginUsernameEl = document.getElementById("loginUsername");
const loginPasswordEl = document.getElementById("loginPassword");

// Tracks the most recently searched route, so Live Availability can be
// refreshed after an Edit or Delete without wrongly showing the whole
// fleet when no search has happened yet this session.
let lastSearchedRoute = null;

// Tracks which bus_id is currently being edited (null = "Add" mode).
let editingBusId = null;

// Updates the Live Route Map to show driving directions between the
// exact source and destination the user searched for.
//
// Uses Google's legacy "saddr/daddr...output=embed" pattern, which does
// not require an API key. If you later obtain a Google Maps API key,
// swap this for the officially supported Embed API instead:
//   https://www.google.com/maps/embed/v1/directions
//     ?origin=<source>&destination=<destination>&mode=driving&key=YOUR_API_KEY
function updateRouteMap(source, destination) {
  const mapUrl =
    `https://www.google.com/maps?saddr=${encodeURIComponent(source)}` +
    `&daddr=${encodeURIComponent(destination)}&output=embed`;
  routeMapFrame.src = mapUrl;
}

// ========== Authentication ==========

// Shows/hides Admin Panel and Login/Logout buttons based on isAdmin.
function applyAuthUI() {
  if (isAdmin) {
    adminSection.classList.remove("hidden");
    logoutBtn.classList.remove("hidden");
    loginBtn.classList.add("hidden");
    loginFormSection.classList.add("hidden");
  } else {
    adminSection.classList.add("hidden");
    logoutBtn.classList.add("hidden");
    loginBtn.classList.remove("hidden");
  }
}

// Checks whether this browser already has an active admin session
// (e.g. after a page refresh) so the UI starts in the correct state
// instead of always assuming logged-out.
async function checkAuthStatus() {
  try {
    const res = await fetch(`${API_BASE}/auth/status`);
    const data = await res.json();
    isAdmin = !!data.is_admin;
  } catch (err) {
    console.error("Failed to check auth status:", err);
    isAdmin = false;
  }
  applyAuthUI();
}

loginBtn.addEventListener("click", () => {
  loginFormSection.classList.remove("hidden");
  loginFormSection.scrollIntoView({ behavior: "smooth", block: "center" });
});

document.getElementById("loginCancelBtn").addEventListener("click", () => {
  loginFormSection.classList.add("hidden");
  loginUsernameEl.value = "";
  loginPasswordEl.value = "";
});

document.getElementById("loginSubmitBtn").addEventListener("click", async () => {
  const username = loginUsernameEl.value.trim();
  const password = loginPasswordEl.value;

  if (!username || !password) {
    alert("❌ Please enter both username and password.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (!res.ok) {
      alert(`❌ ${data.error || "Login failed."}`);
      return;
    }

    isAdmin = true;
    loginUsernameEl.value = "";
    loginPasswordEl.value = "";
    applyAuthUI();
    // Admin Panel just became visible — make sure it shows current data.
    await refreshAdminAndSchedule();
  } catch (err) {
    console.error("Login request failed:", err);
    alert("❌ Unable to reach the server. Please try again.");
  }
});

logoutBtn.addEventListener("click", async () => {
  try {
    await fetch(`${API_BASE}/auth/logout`, { method: "POST" });
  } catch (err) {
    console.error("Logout request failed:", err);
  }
  isAdmin = false;
  // Exit edit mode, if active, since the form is about to be hidden.
  resetAdminForm();
  applyAuthUI();
});

// ========== API Layer ==========
// All bus data now lives in the Flask + SQLite backend. There is no
// local array and no localStorage — every section fetches fresh data
// from the API whenever it needs to render.
const API_BASE = "/api";

// Fetches every bus. Used by Admin Panel and Scheduling.
async function fetchAllBuses() {
  try {
    const res = await fetch(`${API_BASE}/buses`);
    const data = await res.json();
    return data.buses || [];
  } catch (err) {
    console.error("Failed to fetch buses:", err);
    return [];
  }
}

// Fetches buses with a fresh, server-generated passenger_load.
// When source/destination are provided, only buses matching that route
// are returned. Used by Live Availability after a search.
async function fetchLiveBuses(source, destination) {
  try {
    let url = `${API_BASE}/live`;
    if (source && destination) {
      url += `?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    return data.buses || [];
  } catch (err) {
    console.error("Failed to fetch live bus data:", err);
    return [];
  }
}

// Re-fetches all buses and re-renders both Admin Panel and Scheduling.
// Called after Add/Edit/Delete, and once on page load.
async function refreshAdminAndSchedule() {
  const buses = await fetchAllBuses();
  updateAdminPanel(buses);
  updateSchedule(buses);
}

// Re-runs Live Availability against the last searched route, if any.
// Used after Edit/Delete so a changed or removed bus is reflected
// immediately without requiring the admin to search again.
async function refreshLiveIfSearched() {
  if (lastSearchedRoute) {
    await loadLiveBusAvailability(lastSearchedRoute.source, lastSearchedRoute.destination);
  }
}

// ========== Dashboard ==========

// Fetches the four summary numbers for the dashboard cards.
async function fetchDashboardStats() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch dashboard stats:", err);
    return null;
  }
}

// Renders the fetched stats into the four dashboard cards.
function renderDashboard(stats) {
  if (!stats) {
    return;
  }
  document.getElementById("totalBusesCount").textContent = stats.total_buses;
  document.getElementById("activeRoutesCount").textContent = stats.active_routes;
  document.getElementById("availableBusesCount").textContent = stats.available_buses;
  document.getElementById("avgPassengerLoadCount").textContent =
    `${stats.average_passenger_load}%`;
}

// Fetches and renders the dashboard in one call. Run on page load, and
// again after any Add/Edit/Delete so the cards stay in sync automatically.
async function refreshDashboard() {
  const stats = await fetchDashboardStats();
  renderDashboard(stats);
}

// ========== Search Bus Functionality ==========
searchBtn.addEventListener("click", async () => {
  const src = sourceInput.value.trim();
  const dest = destinationInput.value.trim();

  if (!src || !dest) {
    busResult.textContent = "Please enter both source and destination.";
    return;
  }

  // Show the driving route for whatever the user typed, regardless of
  // whether a matching bus is found below.
  updateRouteMap(src, dest);

  // Remember this route so Edit/Delete can refresh Live Availability
  // against it later without needing the admin to search again.
  lastSearchedRoute = { source: src, destination: dest };

  // Live Availability is now route-specific: only buses matching this
  // exact searched route are shown, not the entire fleet.
  await loadLiveBusAvailability(src, dest);

  try {
    const res = await fetch(
      `${API_BASE}/search?source=${encodeURIComponent(src)}&destination=${encodeURIComponent(dest)}`
    );
    const data = await res.json();

    if (!res.ok) {
      // Server-side validation error (e.g. missing query params)
      busResult.textContent = data.error || "Something went wrong.";
      return;
    }

    if (!data.buses || data.buses.length === 0) {
      busResult.textContent = "No matching bus found.";
      return;
    }

    const match = data.buses[0];
    busResult.innerHTML = `
      Best Bus: <strong>${match.bus_id}</strong><br>
      ETA: ${match.eta}<br>
      Route: ${match.route}
    `;
  } catch (err) {
    console.error("Search request failed:", err);
    busResult.textContent = "Unable to reach the server. Please try again.";
  }
});

// ========== Admin + Scheduling ==========

const busIdInputEl = document.getElementById("busIdInput");
const sourceInputAdminEl = document.getElementById("sourceInputAdmin");
const destinationInputAdminEl = document.getElementById("destinationInputAdmin");
const routeInputEl = document.getElementById("routeInput");
const etaInputEl = document.getElementById("etaInput");
const addBusBtn = document.getElementById("addBusBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");

// Clears the form and returns the Admin Panel to "Add" mode.
function resetAdminForm() {
  editingBusId = null;
  busIdInputEl.value = "";
  sourceInputAdminEl.value = "";
  destinationInputAdminEl.value = "";
  routeInputEl.value = "";
  etaInputEl.value = "";

  // Bus ID is only ever editable while adding a brand-new bus.
  busIdInputEl.readOnly = false;
  busIdInputEl.classList.remove("bg-gray-200", "cursor-not-allowed");

  addBusBtn.textContent = "Add Bus";
  cancelEditBtn.classList.add("hidden");
}

// Pre-fills the form with an existing bus's data and switches to "Edit"
// mode. Bus ID stays read-only — only Source, Destination, Route, and
// ETA can be changed, per the Bus Management spec.
function startEditBus(bus) {
  editingBusId = bus.bus_id;

  busIdInputEl.value = bus.bus_id;
  busIdInputEl.readOnly = true;
  busIdInputEl.classList.add("bg-gray-200", "cursor-not-allowed");

  sourceInputAdminEl.value = bus.source || "";
  destinationInputAdminEl.value = bus.destination || "";
  routeInputEl.value = bus.route || "";
  etaInputEl.value = bus.eta || "";

  addBusBtn.textContent = "Update Bus";
  cancelEditBtn.classList.remove("hidden");

  // Scroll the form into view in case the admin clicked Edit further
  // down a long bus list.
  busIdInputEl.scrollIntoView({ behavior: "smooth", block: "center" });
}

cancelEditBtn.addEventListener("click", () => {
  resetAdminForm();
});

// Add Bus / Update Bus — same button, behavior depends on editingBusId.
addBusBtn.addEventListener("click", async () => {
  const id = busIdInputEl.value.trim();
  const source = sourceInputAdminEl.value.trim();
  const destination = destinationInputAdminEl.value.trim();
  const route = routeInputEl.value.trim();
  const eta = etaInputEl.value.trim();

  if (!id || !source || !destination || !route) {
    alert("❌ Please enter Bus ID, Source, Destination, and Route.");
    return;
  }

  if (editingBusId) {
    // ---- Update existing bus (Source, Destination, Route, ETA only) ----
    try {
      const res = await fetch(`${API_BASE}/buses/${encodeURIComponent(editingBusId)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: source,
          destination: destination,
          route: route,
          eta: eta || "N/A"
        })
      });
      const data = await res.json();

      if (!res.ok) {
        alert(`❌ ${data.error || "Failed to update bus."}`);
        return;
      }

      alert(`✅ Bus ${editingBusId} updated successfully.`);
      resetAdminForm();
      await refreshAdminAndSchedule();
      await refreshLiveIfSearched();
      await refreshDashboard();
    } catch (err) {
      console.error("Update bus request failed:", err);
      alert("❌ Unable to reach the server. Please try again.");
    }
  } else {
    // ---- Add new bus ----
    try {
      const res = await fetch(`${API_BASE}/buses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bus_id: id,
          source: source,
          destination: destination,
          route: route,
          eta: eta || "N/A"
        })
      });
      const data = await res.json();

      if (!res.ok) {
        // Server-side error: duplicate bus_id (409), missing fields (400), etc.
        alert(`❌ ${data.error || "Failed to add bus."}`);
        return;
      }

      alert(`✅ Bus ${id} assigned to ${route} added successfully.`);
      resetAdminForm();

      // Re-render Admin Panel and Scheduling, which always show every bus.
      // Live Availability is left as-is — it's tied to whatever route was
      // last searched, and adding a bus doesn't change that search context.
      await refreshAdminAndSchedule();
      await refreshDashboard();
    } catch (err) {
      console.error("Add bus request failed:", err);
      alert("❌ Unable to reach the server. Please try again.");
    }
  }
});

// Deletes a bus after explicit confirmation, then refreshes every
// section that could be affected.
async function deleteBus(busId) {
  const confirmed = confirm(`Delete ${busId}? This cannot be undone.`);
  if (!confirmed) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/buses/${encodeURIComponent(busId)}`, {
      method: "DELETE"
    });
    const data = await res.json();

    if (!res.ok) {
      alert(`❌ ${data.error || "Failed to delete bus."}`);
      return;
    }

    // If the deleted bus was mid-edit, drop back to "Add" mode.
    if (editingBusId === busId) {
      resetAdminForm();
    }

    await refreshAdminAndSchedule();
    await refreshLiveIfSearched();
    await refreshDashboard();
  } catch (err) {
    console.error("Delete bus request failed:", err);
    alert("❌ Unable to reach the server. Please try again.");
  }
}

// Renders the Admin Panel's bus list from a given buses array, with
// Edit and Delete controls per bus. Uses a data-bus-id attribute plus
// one delegated click listener (see below) instead of inline onclick,
// consistent with how this project avoids inline handlers elsewhere.
function updateAdminPanel(buses) {
  const list = document.getElementById("busList");
  list.innerHTML = ""; // Clear existing list
  buses.forEach((bus) => {
    const li = document.createElement("li");
    li.className = "flex items-center justify-between gap-3 py-1";
    li.innerHTML = `
      <span>${bus.bus_id} - ${bus.route}</span>
      <span class="flex gap-2 shrink-0">
        <button type="button" class="text-blue-600 hover:underline text-sm" data-action="edit" data-bus-id="${bus.bus_id}">Edit</button>
        <button type="button" class="text-red-600 hover:underline text-sm" data-action="delete" data-bus-id="${bus.bus_id}">Delete</button>
      </span>
    `;
    list.appendChild(li);
  });
}

// Single delegated listener for all Edit/Delete buttons in the Admin
// list — buttons are re-created on every render, so binding once on
// the stable parent avoids re-attaching listeners each time.
document.getElementById("busList").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const busId = button.dataset.busId;

  if (button.dataset.action === "delete") {
    await deleteBus(busId);
    return;
  }

  if (button.dataset.action === "edit") {
    const buses = await fetchAllBuses();
    const bus = buses.find((b) => b.bus_id === busId);
    if (bus) {
      startEditBus(bus);
    }
  }
});

// Derives a schedule status label from an eta string (e.g. "5 mins").
// Thresholds: <=10 On Schedule, 11-20 Arriving Soon, >20 Delayed.
// If no number can be parsed (e.g. "N/A"), returns an Unknown status
// rather than guessing.
function getScheduleStatus(eta) {
  const match = String(eta || "").match(/\d+/);
  if (!match) {
    return { label: "Unknown", emoji: "⚪", textClass: "text-gray-500" };
  }
  const minutes = parseInt(match[0], 10);
  if (minutes <= 10) {
    return { label: "On Schedule", emoji: "🟢", textClass: "text-green-600" };
  }
  if (minutes <= 20) {
    return { label: "Arriving Soon", emoji: "🟡", textClass: "text-yellow-600" };
  }
  return { label: "Delayed", emoji: "🔴", textClass: "text-red-600" };
}

// Renders the Scheduling section from a given buses array as
// individual, responsive cards.
function updateSchedule(buses) {
  const container = document.getElementById("schedule-updates");
  container.innerHTML = "";
  buses.forEach((bus) => {
    const status = getScheduleStatus(bus.eta);
    const div = document.createElement("div");
    div.className =
      "bus-card transition duration-200 transform hover:-translate-y-1 hover:shadow-xl";
    div.innerHTML = `
      <p class="font-semibold text-blue-700 text-lg">🚌 ${bus.bus_id}</p>
      <p class="mt-2"><span class="font-medium">📍 Route:</span><br>${bus.route}</p>
      <p class="mt-2"><span class="font-medium">⏱ ETA:</span> ${bus.eta}</p>
      <p class="mt-2 font-medium ${status.textClass}">${status.emoji} Status: ${status.label}</p>
    `;
    container.appendChild(div);
  });
}

// Fetches and renders Live Availability for ONE specific route — only
// buses matching the given source/destination are shown, using the
// backend's server-generated, persisted passenger_load.
async function loadLiveBusAvailability(source, destination) {
  const container = document.getElementById("live-bus-list");
  const buses = await fetchLiveBuses(source, destination);
  container.innerHTML = "";

  if (buses.length === 0) {
    container.innerHTML = `<div class="p-4 bg-white shadow rounded">No buses available for this route.</div>`;
    return;
  }

  buses.forEach((bus) => {
    const div = document.createElement("div");
    div.className = "bus-card";
    div.innerHTML = `
      <h4 class="font-semibold text-blue-700">${bus.bus_id}</h4>
      <p>Route: ${bus.route}</p>
      <p>ETA: ${bus.eta}</p>
      <p>Passenger Load: ${bus.passenger_load}%</p>
    `;
    container.appendChild(div);
  });
}

// Load Admin Panel and Scheduling (which always show every bus) on page
// load. Live Availability stays empty/prompted until the user searches.
// Auth status is checked first so the Admin Panel's visibility is
// correct before anything else renders.
window.onload = async () => {
  // Each init step runs independently — if one throws, it's caught and
  // logged here instead of silently aborting the rest of the chain
  // (which is what would leave the dashboard cards stuck at their
  // default "0" values even when later steps would have succeeded).
  try {
    await checkAuthStatus();
  } catch (err) {
    console.error("checkAuthStatus failed:", err);
  }

  try {
    await refreshAdminAndSchedule();
  } catch (err) {
    console.error("refreshAdminAndSchedule failed:", err);
  }

  try {
    await refreshDashboard();
  } catch (err) {
    console.error("refreshDashboard failed:", err);
  }
};