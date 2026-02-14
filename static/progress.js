// static/progress.js

const templatesEl = document.getElementById("workout-templates-data");
const templates = templatesEl ? JSON.parse(templatesEl.textContent) : {};

const STORAGE_KEY = "trainsphere.selected_workout_type";
const DRAFT_KEY_PREFIX = "trainsphere.progress_draft.";

function isEditMode() {
  const rows = document.getElementById("exerciseRows");
  return rows && rows.dataset.editMode === "1";
}

function deriveCategory(type) {
  const t = (type || "").toLowerCase();
  if (t.startsWith("strength")) return "Strength";
  if (t.startsWith("cardio")) return "Cardio";
  if (t.startsWith("hiit")) return "HIIT";
  if (t.includes("yoga") || t.includes("mobility")) return "Mobility";
  return "General";
}

function rowHTML(ex) {
  const name = ex?.name ?? "";
  const sets = ex?.sets ?? "";
  const reps = ex?.reps ?? "";
  const w = ex?.weight_kg ?? "";

  return `
    <div class="card" style="box-shadow:none;margin-top:10px;">
      <label>Exercise name</label>
      <input name="exercise_name[]" value="${String(name).replaceAll('"','&quot;')}" required>

      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
        <div>
          <label>Sets</label>
          <input name="sets[]" type="number" min="1" value="${sets}">
        </div>
        <div>
          <label>Reps</label>
          <input name="reps[]" type="number" min="1" value="${reps}">
        </div>
        <div>
          <label>Weight (kg)</label>
          <input name="weight_kg[]" type="number" step="0.5" value="${w}">
        </div>
      </div>
    </div>
  `;
}

function draftKey(type) {
  return DRAFT_KEY_PREFIX + (type || "");
}

function readDraft(type) {
  try {
    const raw = localStorage.getItem(draftKey(type));
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function writeDraft(type, data) {
  try {
    localStorage.setItem(draftKey(type), JSON.stringify(data));
  } catch (e) {}
}

function collectMeta() {
  return {
    category: document.getElementById("workoutCategory")?.value || "",
    duration_minutes: document.querySelector('input[name="duration_minutes"]')?.value || "",
    performance_rating: document.querySelector('input[name="performance_rating"]')?.value || "",
    feeling_rating: document.querySelector('input[name="feeling_rating"]')?.value || "",
    notes: document.querySelector('textarea[name="notes"]')?.value || "",
    workout_date: document.getElementById("workoutDate")?.value || ""
  };
}

function restoreMeta(draft) {
  const catEl = document.getElementById("workoutCategory");
  const dateEl = document.getElementById("workoutDate");
  const durEl = document.querySelector('input[name="duration_minutes"]');
  const perfEl = document.querySelector('input[name="performance_rating"]');
  const feelEl = document.querySelector('input[name="feeling_rating"]');
  const notesEl = document.querySelector('textarea[name="notes"]');

  if (!draft) {
    if (dateEl) dateEl.value = "";
    if (durEl) durEl.value = "";
    if (perfEl) perfEl.value = "";
    if (feelEl) feelEl.value = "";
    if (notesEl) notesEl.value = "";
    return;
  }

  if (catEl && draft.category) {
    for (const opt of catEl.options) {
      if (opt.value === draft.category) {
        catEl.value = draft.category;
        break;
      }
    }
  }
  if (durEl) durEl.value = draft.duration_minutes || "";
  if (perfEl) perfEl.value = draft.performance_rating || "";
  if (feelEl) feelEl.value = draft.feeling_rating || "";
  if (notesEl) notesEl.value = draft.notes || "";
  if (dateEl && draft.workout_date) dateEl.value = draft.workout_date;
}

function collectExercises() {
  const names = Array.from(document.querySelectorAll('input[name="exercise_name[]"]')).map(x => x.value);
  const sets = Array.from(document.querySelectorAll('input[name="sets[]"]')).map(x => x.value);
  const reps = Array.from(document.querySelectorAll('input[name="reps[]"]')).map(x => x.value);
  const w = Array.from(document.querySelectorAll('input[name="weight_kg[]"]')).map(x => x.value);

  const ex = [];
  for (let i = 0; i < names.length; i++) {
    const n = (names[i] || "").trim();
    if (!n && !sets[i] && !reps[i] && !w[i]) continue;
    ex.push({ name: n, sets: sets[i] || "", reps: reps[i] || "", weight_kg: w[i] || "" });
  }
  return ex;
}

let draftTimer = null;
function scheduleDraftSave() {
  if (draftTimer) clearTimeout(draftTimer);
  draftTimer = setTimeout(saveDraftNow, 250);
}

function saveDraftNow() {
  const type = document.getElementById("workoutType")?.value || "";
  const data = { ...collectMeta(), exercises: collectExercises(), saved_at: new Date().toISOString() };
  writeDraft(type, data);
}

function loadTemplate() {
  const typeEl = document.getElementById("workoutType");
  if (!typeEl) return;

  const type = typeEl.value;

  // remember selected type
  try { localStorage.setItem(STORAGE_KEY, type); } catch (e) {}

  const cat = document.getElementById("workoutCategory");
  if (cat && !cat.dataset.userChanged) {
    const derived = deriveCategory(type);
    for (const opt of cat.options) {
      if (opt.value === derived) { cat.value = derived; break; }
    }
  }

  const container = document.getElementById("exerciseRows");
  if (!container) return;

  container.innerHTML = "";

  const draft = readDraft(type);
  if (draft && Array.isArray(draft.exercises) && draft.exercises.length) {
    draft.exercises.forEach(ex => container.insertAdjacentHTML("beforeend", rowHTML(ex)));
    restoreMeta(draft);
  } else {
    const list = templates[type] || [];
    list.forEach(ex => container.insertAdjacentHTML("beforeend", rowHTML(ex)));
    restoreMeta(null);
  }
}

function clearDraft() {
  const type = document.getElementById("workoutType")?.value || "";
  try { localStorage.removeItem(draftKey(type)); } catch (e) {}

  // In edit mode we don't auto-load templates on init, but Clear draft should still reset UI.
  loadTemplate();
}

// expose functions for inline HTML handlers
window.loadTemplate = loadTemplate;
window.clearDraft = clearDraft;

// init
(function init() {
  // mark user-changed category
  const cat = document.getElementById("workoutCategory");
  if (cat) cat.addEventListener("change", () => { cat.dataset.userChanged = "1"; });

  const form = document.getElementById("workoutForm");
  if (form) {
    form.addEventListener("input", scheduleDraftSave);
    form.addEventListener("change", scheduleDraftSave);
    form.addEventListener("submit", () => {
      const type = document.getElementById("workoutType")?.value || "";
      try { localStorage.removeItem(draftKey(type)); } catch (e) {}
    });
  }

  // if editing an existing workout, do NOT overwrite server-rendered exercise rows on first load
  if (isEditMode()) return;

  // restore last selected type
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    const typeEl = document.getElementById("workoutType");
    if (typeEl && saved && templates[saved]) typeEl.value = saved;
  } catch (e) {}

  loadTemplate();
})();
