// Google Trends: download ONE request (one city x one request letter).
// Runs inside `ego-browser nodejs`. Do not run it directly: use
//   src/trends/download_round.sh
// which calls this file once per request (9 times) with a pause in between.
// The wrapper puts a line like
//   const MWM = { root: "/abs/project", city: "hk", request: "A" };
// in front of this file before piping it to the browser runtime.
//
// What it does, in order:
//   1. opens the explore page for the request in the one task Space ("mwm-trends")
//   2. stops if Google shows a captcha, a 429 page, a consent wall, or an error in the chart
//   3. checks ON THE PAGE that each set is read as one combined "Search term" item,
//      that geography, dates, category and search type are right, and that the chart
//      is "Interest over time" with one point per month
//   4. reads the "Note" markers on the chart (dates when Google changed its data)
//   5. clicks the chart's own CSV button and saves the file, bytes unchanged
//   6. appends a row to data/raw/trends/manifest.csv and a line to
//      data/interim/trends/page_checks.md, and writes a JSON log
// It never signs in, never clicks consent, and never retries around a block.
// Last line printed: MWM_STATUS=<ok|no_data|check_failed|blocked|consent_wall|timeout|error>

const fs = await import("node:fs/promises");
const crypto = await import("node:crypto");
const path = await import("node:path");

const ROOT = MWM.root;
const city = MWM.city;
const request = MWM.request;
const RAW = path.join(ROOT, "data/raw/trends");
const INTERIM = path.join(ROOT, "data/interim/trends");
const LOGS = path.join(INTERIM, "round_logs");
const SCREENS = path.join(INTERIM, "screens");
const SPACE_FILE = path.join(INTERIM, "taskspace.txt");
const SPACE_NAME = "mwm-trends";

const cfg = JSON.parse(await fs.readFile(path.join(ROOT, "src/trends/term_sets.json"), "utf8"));
const cats = cfg.requests[request];
const items = cats.map((c) => cfg.sets[city][c]);
const geo = cfg.geos[city];
const url =
  "https://trends.google.com/trends/explore?date=" +
  encodeURIComponent(cfg.date) +
  "&geo=" + geo +
  "&q=" + items.map((s) => encodeURIComponent(s)).join(",") +
  "&hl=en-US";

function utcStamp(d) {
  return d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
}
function csvCell(s) {
  s = String(s ?? "");
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}
function expectedMonths() {
  const [a, b] = cfg.date.split(" ");
  const [y1, m1] = a.split("-").map(Number);
  const [y2, m2] = b.split("-").map(Number);
  return (y2 - y1) * 12 + (m2 - m1) + 1;
}
function expectedDatePickerText() {
  // page shows m/d/yy - m/d/yy
  return cfg.date
    .split(" ")
    .map((d) => {
      const [y, m, dd] = d.split("-").map(Number);
      return `${m}/${dd}/${String(y).slice(2)}`;
    })
    .join(" - ");
}
const norm = (s) => String(s ?? "").replace(/[‪-‮‎‏]/g, "").replace(/\s+/g, " ").trim();

await fs.mkdir(RAW, { recursive: true });
await fs.mkdir(LOGS, { recursive: true });
await fs.mkdir(SCREENS, { recursive: true });

const result = {
  city, request, geo, categories: cats, items, source_url: url,
  started_utc: new Date().toISOString(),
  status: "error", problems: [],
};

async function finishAndReport(page) {
  const stamp = result.download_id || utcStamp(new Date());
  // screenshot as evidence of what the page showed (best effort)
  if (page) {
    try {
      const shot = path.join(SCREENS, `${city}_${request}_${stamp}.png`);
      await page.screenshot({ path: shot });
      result.screenshot = path.relative(ROOT, shot);
    } catch (e) {
      result.screenshot_error = String(e && e.message ? e.message : e).slice(0, 200);
    }
  }
  result.finished_utc = new Date().toISOString();
  await fs.writeFile(path.join(LOGS, `${city}_${request}_${stamp}.json`), JSON.stringify(result, null, 1));

  // one line per request in page_checks.md
  const pc = path.join(INTERIM, "page_checks.md");
  let head = "";
  try { await fs.access(pc); } catch {
    head =
      "# Google Trends page checks\n\n" +
      "One line per request, written by src/trends/download_round.mjs just before the CSV export. " +
      "It records what the Trends page itself showed. Full detail is in round_logs/<city>_<request>_<time>.json.\n\n";
  }
  const c = result.check || {};
  const chipTxt = (c.chips || []).map((x, i) => `[${i + 1}] "${x.value}" (${x.desc})`).join("; ");
  const noteTxt = (result.notes || []).map((n) => n.text || `unread note at x=${n.x}`).join(" | ");
  const line =
    `- ${result.finished_utc} | ${city} ${request} | status: ${result.status}` +
    ` | items as one combined search term each: ${c.chips_ok === true ? "YES (5 of 5)" : c.chips_ok === false ? "NO" : "not checked"}` +
    ` | chips: ${chipTxt || "none read"}` +
    ` | geography shown: "${c.geo_shown ?? ""}" (wanted "${cfg.geo_labels[city]}", url geo=${c.url_geo ?? ""})` +
    ` | dates shown: "${c.date_shown ?? ""}"` +
    ` | category: "${c.category_shown ?? ""}" | search type: "${c.property_shown ?? ""}"` +
    ` | chart: "${c.chart_title ?? ""}", ${c.n_points ?? "?"} points, ${c.first_point ?? "?"} to ${c.last_point ?? "?"}, monthly: ${c.monthly === true ? "yes" : c.monthly === false ? "NO" : "?"}` +
    ` | chart legend matches the five sets: ${c.legend_ok === true ? "yes" : c.legend_ok === false ? "NO" : "?"}` +
    ` | notes on chart (${(result.notes || []).length}): ${noteTxt || "none"}` +
    (result.chart_message ? ` | Trends message in chart: "${result.chart_message}"` : "") +
    (result.block_evidence ? ` | block evidence: ${JSON.stringify(result.block_evidence)}` : "") +
    (result.problems.length ? ` | problems: ${result.problems.join("; ")}` : "") +
    (result.file ? ` | saved: ${result.file}` : " | no file saved") +
    "\n";
  await fs.appendFile(pc, head + line);

  console.log(JSON.stringify({ status: result.status, file: result.file || null, problems: result.problems, notes: (result.notes || []).map((n) => n.text) }));
  console.log("MWM_STATUS=" + result.status);
}

let page = null;
try {
  // ---- the one task Space ----
  let task = null;
  let wantedId = null;
  try { wantedId = Number((await fs.readFile(SPACE_FILE, "utf8")).trim()); } catch {}
  const spaces = await listTaskSpaces();
  let entry = Number.isFinite(wantedId) ? spaces.find((s) => s.id === wantedId && s.name === SPACE_NAME) : null;
  if (!entry) entry = spaces.find((s) => s.name === SPACE_NAME) || null;
  if (!entry) {
    task = await taskSpace(SPACE_NAME);
  } else if (entry.ownership === "user") {
    task = await claimTaskSpace(entry.id);
  } else if (entry.ownership === "agentDelegatedToUser") {
    throw new Error("task Space is handed to the user; not taking it back");
  } else {
    task = await taskSpace(entry.id);
  }
  await fs.writeFile(SPACE_FILE, String(task.spaceId) + "\n");
  result.task_space_id = task.spaceId;
  page = (await task.pages())[0] ?? (await task.adopt((await task.tabs())[0].page));

  // ---- load the request ----
  await page.goto(url, { timeout: 60000 });

  const probe = () =>
    page.evaluate(() => {
      const body = (document.body && document.body.innerText) || "";
      const w = document.querySelector('widget[type="fe_line_chart"]');
      let rows = 0;
      let lineErr = "";
      if (w) {
        const tables = [...w.querySelectorAll("table")];
        rows = Math.max(0, ...tables.map((t) => t.rows.length));
        const e = w.querySelector(".widget-error");
        if (e) lineErr = (e.innerText || "").replace(/\s+/g, " ").trim();
      }
      let api = [];
      try {
        api = performance
          .getEntriesByType("resource")
          .filter((r) => r.name.includes("/trends/api/"))
          .map((r) => ({ path: r.name.split("?")[0].replace(/^https?:\/\/[^/]+/, ""), status: r.responseStatus }));
      } catch (e) {}
      return {
        href: location.href,
        title: document.title,
        // A captcha means a challenge the visitor has to solve: Google's /sorry/ page, its
        // "unusual traffic" text, or a VISIBLE reCAPTCHA frame. Every Trends page also carries an
        // invisible reCAPTCHA badge (a hidden frame inside .grecaptcha-logo). That badge asks for
        // nothing and is on the page when everything works, so it does not count.
        captcha:
          /\/sorry\//.test(location.href) ||
          /unusual traffic|not a robot|captcha/i.test(body.slice(0, 5000)) ||
          !!document.querySelector('#captcha-form, form[action*="sorry"]') ||
          [...document.querySelectorAll('iframe[src*="recaptcha"]')].some((f) => {
            if (f.closest(".grecaptcha-badge, .grecaptcha-logo")) return false;
            const cs = getComputedStyle(f);
            const b = f.getBoundingClientRect();
            return cs.visibility === "visible" && cs.display !== "none" && b.width > 20 && b.height > 20 && b.bottom > 0 && b.right > 0;
          }),
        recaptcha_frames: [...document.querySelectorAll('iframe[src*="recaptcha"]')].map((f) => ({
          kind: (f.getAttribute("src") || "").includes("bframe") ? "challenge frame" : "badge frame",
          in_badge: !!f.closest(".grecaptcha-badge, .grecaptcha-logo"),
          visibility: getComputedStyle(f).visibility,
        })),
        tooMany: /\b429\b|too many requests/i.test(document.title) || /Error 429|too many requests/i.test(body.slice(0, 3000)),
        consent: /consent\.google\./.test(location.href),
        signin: /accounts\.google\.[^/]+\/(v3\/)?signin|ServiceLogin/.test(location.href),
        hasWidget: !!w,
        rows,
        lineErr,
        api,
      };
    });

  let st = null;
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    await page.waitForTimeout(2000);
    st = await probe();
    if (st.captcha || st.tooMany || st.consent || st.signin) break;
    if (st.rows >= 3 || st.lineErr) break;
    if (st.api.some((a) => a.status === 429)) break;
  }
  result.api_statuses = st ? st.api : [];
  result.recaptcha_frames = st ? st.recaptcha_frames : [];
  result.page_title = st ? st.title : "";

  if (!st) throw new Error("page gave no state");
  if (st.consent || st.signin) {
    result.status = "consent_wall";
    result.block_evidence = { href: st.href, title: st.title, kind: st.consent ? "consent page" : "sign-in page" };
    await finishAndReport(page);
  } else if (st.captcha || st.tooMany || st.api.some((a) => a.status === 429)) {
    result.status = "blocked";
    result.block_evidence = {
      href: st.href, title: st.title, captcha: st.captcha, too_many_requests_page: st.tooMany,
      api_429: st.api.filter((a) => a.status === 429).map((a) => a.path),
    };
    await finishAndReport(page);
  } else if (st.lineErr && st.rows < 3) {
    result.chart_message = st.lineErr;
    if (/enough data/i.test(st.lineErr)) {
      result.status = "no_data"; // Trends says the request has too little data. Recorded, nothing altered.
    } else {
      result.status = "blocked"; // an error box in the chart, usually rate limiting. Stop the round.
      result.block_evidence = { href: st.href, title: st.title, chart_error: st.lineErr };
    }
    await finishAndReport(page);
  } else if (st.rows < 3) {
    result.status = "timeout";
    result.block_evidence = { href: st.href, title: st.title, note: "chart did not appear within 60 s" };
    await finishAndReport(page);
  } else {
    // ---- the on-page check ----
    await page.waitForTimeout(2500); // let the chart finish drawing
    const seen = await page.evaluate(() => {
      const clean = (s) => String(s ?? "").replace(/[‪-‮‎‏]/g, "").replace(/\s+/g, " ").trim();
      const w = document.querySelector('widget[type="fe_line_chart"]');
      w.scrollIntoView({ block: "center" });
      const chips = [...document.querySelectorAll("explore-search-term")].map((n) => {
        const i = n.querySelector("input");
        return { value: clean(i ? i.value : ""), desc: clean((n.querySelector(".search-term-entity-desc") || {}).innerText) };
      });
      const hp = [...document.querySelectorAll(".compare-pickers hierarchy-picker")].map((n) => clean(n.innerText));
      const sel = [...document.querySelectorAll(".compare-pickers md-select")].map((n) => clean(n.innerText));
      const tables = [...w.querySelectorAll("table")];
      const big = tables.sort((a, b) => b.rows.length - a.rows.length)[0];
      const small = tables.find((t) => t !== big);
      const dates = [...big.rows].slice(1).map((r) => clean(r.cells[0].innerText));
      const legend = small ? [...small.rows[0].cells].slice(1).map((c) => clean(c.innerText)) : [];
      const averages = small && small.rows[1] ? [...small.rows[1].cells].slice(1).map((c) => clean(c.innerText)) : [];
      const title = clean((w.querySelector(".fe-line-chart-header-title") || {}).innerText).replace(/\s*help_outline\s*$/, "");
      const nExport = w.querySelectorAll("button.export").length;
      const err = w.querySelector(".widget-error");
      return {
        chips, geo_shown: hp[0] || "", category_shown: hp[1] || "",
        date_shown: clean((document.querySelector("custom-date-picker") || {}).innerText),
        property_shown: sel[sel.length - 1] || "",
        dates, legend, averages, title, nExport,
        chart_message: err ? clean(err.innerText) : "",
        href: location.href,
      };
    });

    const check = {};
    check.chips = seen.chips;
    check.chips_ok =
      seen.chips.length === items.length &&
      seen.chips.every((c, i) => norm(c.value) === norm(items[i]) && c.desc === "Search term");
    check.geo_shown = seen.geo_shown;
    check.url_geo = (seen.href.match(/[?&]geo=([^&]+)/) || [])[1] || "";
    check.geo_ok = seen.geo_shown === cfg.geo_labels[city] && check.url_geo === geo;
    check.date_shown = seen.date_shown;
    check.category_shown = seen.category_shown;
    check.property_shown = seen.property_shown;
    check.chart_title = seen.title;
    check.n_points = seen.dates.length;
    check.first_point = seen.dates[0];
    check.last_point = seen.dates[seen.dates.length - 1];
    // monthly: every point is the first of a month and the months are consecutive
    const parsed = seen.dates.map((d) => new Date(d + " UTC"));
    let monthly = parsed.length > 1 && parsed.every((d) => !isNaN(d) && d.getUTCDate() === 1);
    for (let i = 1; monthly && i < parsed.length; i++) {
      const gap = (parsed[i].getUTCFullYear() - parsed[i - 1].getUTCFullYear()) * 12 + (parsed[i].getUTCMonth() - parsed[i - 1].getUTCMonth());
      if (gap !== 1) monthly = false;
    }
    check.monthly = monthly;
    const [d1, d2] = cfg.date.split(" ");
    const ym = (d) => (isNaN(d) ? "" : d.toISOString().slice(0, 7));
    check.range_ok =
      seen.date_shown === expectedDatePickerText() &&
      ym(parsed[0]) === d1.slice(0, 7) &&
      ym(parsed[parsed.length - 1]) === d2.slice(0, 7) &&
      parsed.length === expectedMonths();
    check.legend = seen.legend;
    check.legend_ok = seen.legend.length === items.length && seen.legend.every((l, i) => norm(l) === norm(items[i]));
    check.page_averages = seen.averages;
    check.filters_ok = seen.category_shown === "All categories" && seen.property_shown === "Web Search";
    check.title_ok = seen.title === "Interest over time";
    result.check = check;
    if (seen.chart_message) result.chart_message = seen.chart_message;

    if (!check.chips_ok) result.problems.push("the five chips are not the five sets as single search terms");
    if (!check.geo_ok) result.problems.push(`geography shown "${seen.geo_shown}" (url geo=${check.url_geo}), wanted "${cfg.geo_labels[city]}" (${geo})`);
    if (!check.range_ok) result.problems.push(`date range: picker "${seen.date_shown}", ${parsed.length} points ${check.first_point} to ${check.last_point}; wanted ${expectedDatePickerText()} and ${expectedMonths()} months`);
    if (!check.monthly) result.problems.push("chart points are not one per month");
    if (!check.legend_ok) result.problems.push("chart legend does not list the five sets");
    if (!check.filters_ok) result.problems.push(`filters: category "${seen.category_shown}", search type "${seen.property_shown}"`);
    if (!check.title_ok) result.problems.push(`chart title "${seen.title}"`);
    if (seen.nExport !== 1) result.problems.push(`found ${seen.nExport} CSV buttons in the chart`);

    // ---- the Note markers (read only; they never block the export) ----
    result.notes = [];
    try {
      const pts = await page.evaluate(() => {
        const w = document.querySelector('widget[type="fe_line_chart"]');
        return [...w.querySelectorAll("svg text")]
          .filter((t) => t.textContent.trim() === "Note")
          .map((t) => { const b = t.getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; });
      });
      for (const p of pts) {
        let text = "";
        try {
          await page.mouse.move(p.x - 8, p.y, { label: "hover chart note marker" });
          await page.waitForTimeout(1200);
          text = await page.evaluate(() => {
            const n = document.querySelector(".fe-line-chart-tooltip.note-tooltip, .note-tooltip");
            return n ? (n.innerText || n.textContent || "").replace(/\s+/g, " ").trim() : "";
          });
        } catch (e) {}
        result.notes.push({ x: Math.round(p.x), text });
      }
      // move the pointer off the chart
      await page.mouse.move(40, 400, { label: "move pointer off chart" });
    } catch (e) {
      result.problems.push("could not read note markers: " + String(e && e.message ? e.message : e).slice(0, 120));
    }

    const pass = check.chips_ok && check.geo_ok && check.range_ok && check.monthly && check.legend_ok && check.filters_ok && check.title_ok && seen.nExport === 1;
    if (!pass) {
      result.status = "check_failed"; // nothing is exported when the page check fails
      await finishAndReport(page);
    } else {
      // ---- export with the page's own CSV button ----
      const downloadPromise = page.waitForEvent("download", { timeout: 30000 });
      await page.click('widget[type="fe_line_chart"] button.export', { label: "download interest over time CSV" });
      const download = await downloadPromise;
      const now = new Date();
      const stamp = utcStamp(now);
      const rel = `data/raw/trends/${city}_${request}_${stamp}.csv`;
      const abs = path.join(ROOT, rel);
      await download.saveAs(abs);
      const bytes = await fs.readFile(abs);
      const sha = crypto.createHash("sha256").update(bytes).digest("hex");
      result.download_id = stamp;
      result.file = rel;
      result.retrieved_utc = now.toISOString().replace(/\.\d{3}Z$/, "Z");
      result.sha256 = sha;
      result.bytes = bytes.length;
      result.suggested_filename = download.suggestedFilename();
      // light look at the file (nothing is changed in it)
      const text = bytes.toString("utf8").replace(/^﻿/, "");
      const lines = text.split(/\r?\n/).filter((l) => l.trim() !== "");
      const dataLines = lines.filter((l) => /^\d{4}-\d{2}/.test(l));
      result.file_data_rows = dataLines.length;
      result.file_header = lines.find((l) => /^(Month|Time|Week|Day)\b/.test(l)) || "";
      if (dataLines.length !== expectedMonths()) result.problems.push(`file has ${dataLines.length} monthly rows, expected ${expectedMonths()}`);
      result.status = "ok";

      const mf = path.join(RAW, "manifest.csv");
      try { await fs.access(mf); } catch { await fs.writeFile(mf, "path,source_url,retrieved_utc,sha256,status,note\n"); }
      const note =
        `Google Trends "Interest over time" CSV, request ${request} (${cats.join("+")}), geo ${geo}; ` +
        `page check passed; ${dataLines.length} monthly rows; bytes unchanged; task Space ${task.spaceId}`;
      await fs.appendFile(mf, [rel, url, result.retrieved_utc, sha, "ok", note].map(csvCell).join(",") + "\n");
      await finishAndReport(page);
    }
  }
} catch (e) {
  result.status = "error";
  result.problems.push(String(e && e.stack ? e.stack : e).slice(0, 600));
  try { await finishAndReport(page); } catch (e2) {
    console.log("could not write report: " + String(e2));
    console.log("MWM_STATUS=error");
  }
}
