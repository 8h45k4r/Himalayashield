/* Himalayashield operations console v0 (ADR 0005).
 * Dependency-free live polling of public FDSN services. Hard rule: a frozen
 * panel must never look live — every panel carries a data-age stamp and
 * flips to the purple OFFLINE state on failure or staleness.
 */
"use strict";
(function () {
  var BBOX = { minlatitude: 26.0, maxlatitude: 31.5,
               minlongitude: 78.0, maxlongitude: 90.5 };
  var USGS = "https://earthquake.usgs.gov/fdsnws/event/1/query";
  var IRIS = "https://service.iris.edu/fdsnws/station/1/query";
  var POLL_MS = 60000, STALE_MS = 5 * 60000, WINDOW_H = 48, MIN_MAG = 2.0;

  var lastOk = null, events = [];

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function utc(d) {
    return pad(d.getUTCDate()) + " " +
      ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.getUTCMonth()] +
      " " + pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + " UTC";
  }
  function ageText(ms) {
    if (ms < 90000) return Math.round(ms / 1000) + " s";
    if (ms < 5400000) return Math.round(ms / 60000) + " min";
    return (ms / 3600000).toFixed(1) + " h";
  }

  function setFeedState(state, ageMs) {
    var chip = $("feed-chip");
    if (state === "live") {
      chip.className = "chip chip-live";
      chip.textContent = "● LIVE · data age " + ageText(ageMs);
    } else if (state === "stale") {
      chip.className = "chip chip-offline";
      chip.textContent = "⊘ STALE · last data " + ageText(ageMs) + " ago";
    } else {
      chip.className = "chip chip-offline";
      chip.textContent = "⊘ FEED OFFLINE · fetch failed";
    }
  }

  function drawChart() {
    var w = 720, h = 220, pad_ = 40;
    var now = Date.now(), start = now - WINDOW_H * 3600000;
    var lo = MIN_MAG, hi = 6.0;
    for (var i = 0; i < events.length; i++) {
      if (events[i].mag + 0.5 > hi) hi = events[i].mag + 0.5;
    }
    function X(t) { return pad_ + (t - start) / (now - start) * (w - 2 * pad_); }
    function Y(m) { return h - pad_ - (m - lo) / (hi - lo) * (h - 2 * pad_); }
    var s = [];
    var m = Math.ceil(lo);
    for (; m <= hi; m++) {
      var y = Y(m).toFixed(1);
      s.push('<line x1="' + pad_ + '" y1="' + y + '" x2="' + (w - pad_) +
        '" y2="' + y + '" stroke="var(--border-subtle)" stroke-width="1"/>');
      s.push('<text x="' + (pad_ - 8) + '" y="' + (+y + 4) +
        '" text-anchor="end" font-size="11" fill="var(--text-secondary)">M' + m + "</text>");
    }
    for (var hrs = 0; hrs <= WINDOW_H; hrs += 12) {
      var t = start + hrs * 3600000, x = X(t).toFixed(1);
      var d = new Date(t);
      s.push('<line x1="' + x + '" y1="' + (h - pad_) + '" x2="' + x + '" y2="' +
        (h - pad_ + 5) + '" stroke="var(--text-secondary)" stroke-width="1"/>');
      s.push('<text x="' + x + '" y="' + (h - pad_ + 18) +
        '" text-anchor="middle" font-size="11" fill="var(--text-secondary)">' +
        pad(d.getUTCDate()) + "/" + pad(d.getUTCMonth() + 1) + " " +
        pad(d.getUTCHours()) + "h</text>");
    }
    for (i = 0; i < events.length; i++) {
      var e = events[i];
      var r = (2.5 + (e.mag - lo) * 1.4).toFixed(1);
      s.push('<circle cx="' + X(e.time).toFixed(1) + '" cy="' + Y(e.mag).toFixed(1) +
        '" r="' + r + '" fill="var(--link)" fill-opacity="0.55" ' +
        'stroke="var(--bg)" stroke-width="2"><title>' +
        esc("M" + e.mag.toFixed(1) + " — " + e.place + " — " + utc(new Date(e.time))) +
        "</title></circle>");
    }
    $("chart").innerHTML =
      '<svg viewBox="0 0 ' + w + " " + h + '" width="' + w + '" role="img" ' +
      'aria-label="Catalogued events, last ' + WINDOW_H + ' hours">' + s.join("") + "</svg>";
  }

  function renderTable() {
    var rows = [];
    for (var i = events.length - 1; i >= 0 && rows.length < 15; i--) {
      var e = events[i];
      rows.push("<tr><td>" + utc(new Date(e.time)) + '</td><td class="num">' +
        e.mag.toFixed(1) + '</td><td class="num">' +
        (e.depth == null ? "—" : e.depth.toFixed(0)) + "</td><td>" +
        esc(e.place) + "</td></tr>");
    }
    $("events-body").innerHTML = rows.join("") ||
      '<tr><td colspan="4">No catalogued events M≥' + MIN_MAG +
      " in the last " + WINDOW_H + " hours.</td></tr>";
    $("event-count").textContent = String(events.length);
  }

  function poll() {
    var startIso = new Date(Date.now() - WINDOW_H * 3600000)
      .toISOString().slice(0, 19);
    var url = USGS + "?format=geojson&orderby=time-asc&minmagnitude=" + MIN_MAG +
      "&starttime=" + startIso +
      "&minlatitude=" + BBOX.minlatitude + "&maxlatitude=" + BBOX.maxlatitude +
      "&minlongitude=" + BBOX.minlongitude + "&maxlongitude=" + BBOX.maxlongitude;
    fetch(url, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (gj) {
      events = [];
      var feats = gj.features || [];
      for (var i = 0; i < feats.length; i++) {
        var p = feats[i].properties || {};
        var g = (feats[i].geometry || {}).coordinates || [];
        if (p.mag == null || p.time == null) continue;
        events.push({ time: +p.time, mag: +p.mag,
          depth: g.length > 2 && g[2] != null ? +g[2] : null,
          place: String(p.place || "unknown location") });
      }
      lastOk = Date.now();
      drawChart();
      renderTable();
    }).catch(function () {
      if (lastOk === null) setFeedState("offline");
    });
  }

  function loadStations() {
    var url = IRIS + "?format=text&level=station&endafter=" +
      new Date().toISOString().slice(0, 10) +
      "&minlatitude=" + BBOX.minlatitude + "&maxlatitude=" + BBOX.maxlatitude +
      "&minlongitude=" + BBOX.minlongitude + "&maxlongitude=" + BBOX.maxlongitude;
    fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    }).then(function (txt) {
      var lines = txt.split("\n"), rows = [];
      for (var i = 0; i < lines.length; i++) {
        if (!lines[i] || lines[i].charAt(0) === "#") continue;
        var f = lines[i].split("|");
        if (f.length < 4) continue;
        rows.push("<tr><td>" + esc(f[0]) + "</td><td>" + esc(f[1]) +
          '</td><td class="num">' + esc((+f[2]).toFixed(2)) + ", " +
          esc((+f[3]).toFixed(2)) + "</td><td>" + esc(f[5] || "") + "</td></tr>");
      }
      $("station-count").textContent = String(rows.length);
      $("stations-body").innerHTML = rows.join("") ||
        '<tr><td colspan="4">None registered in the box.</td></tr>';
      var chip = $("station-chip");
      chip.className = "chip chip-unverified";
      chip.textContent = "✱ METADATA ONLY · existence, not live health";
    }).catch(function () {
      var chip = $("station-chip");
      chip.className = "chip chip-offline";
      chip.textContent = "⊘ OFFLINE · station service unreachable";
    });
  }

  function tick() {
    if (lastOk !== null) {
      var age = Date.now() - lastOk;
      setFeedState(age > STALE_MS ? "stale" : "live", age);
    }
    $("clock").textContent = utc(new Date());
  }

  poll();
  loadStations();
  setInterval(poll, POLL_MS);
  setInterval(tick, 1000);
  tick();
})();
