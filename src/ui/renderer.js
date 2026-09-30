/**
 * SHUCHI renderer — TRL-4 stub.
 * Talks to main.js over IPC channel `scan-file`; degrades gracefully
 * when run outside Electron (plain browser preview).
 */
(function () {
  'use strict';

  let ipcRenderer = null;
  try {
    const electron = require('electron');
    ipcRenderer = electron && electron.ipcRenderer ? electron.ipcRenderer : null;
  } catch (e) {
    ipcRenderer = null; // plain browser — use mock rows
  }

  function mockResult(name) {
    return {
      input: name,
      verdict: 'CLEAN_REBUILT (mock)',
      scan_results: 'CLEAN (mock)',
      rebuild_status: 'REBUILT (mock)',
    };
  }

  function renderRows(rows) {
    const tbody = document.getElementById('file-tbody');
    tbody.innerHTML = '';
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="4">No files scanned yet.</td></tr>';
      return;
    }
    for (const r of rows) {
      const tr = document.createElement('tr');
      const scanText = Array.isArray(r.scan_results)
        ? r.scan_results.map((s) => s.engine + ': ' + s.status).join('; ')
        : String(r.scan_results || r.verdict || '—');
      const cells = [
        r.input || r.name || '—',
        r.mime_type || r.type || '—',
        scanText,
        r.rebuild_status || r.verdict || '—',
      ];
      for (const c of cells) {
        const td = document.createElement('td');
        td.textContent = c;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }

  const scanned = [];

  async function scanOne(name) {
    if (ipcRenderer) {
      try {
        const res = await ipcRenderer.invoke('scan-file', name);
        return res;
      } catch (e) {
        return { input: name, verdict: 'ERROR', scan_results: String(e), rebuild_status: '—' };
      }
    }
    return mockResult(name); // no Electron runtime — mock for preview
  }

  document.addEventListener('DOMContentLoaded', () => {
    const picker = document.getElementById('file-picker');
    const scanBtn = document.getElementById('scan-btn');
    const printBtn = document.getElementById('print-btn');

    scanBtn.addEventListener('click', async () => {
      const files = (picker && picker.files) ? Array.from(picker.files) : [];
      if (!files.length) {
        renderRows([{ input: '(no file chosen)', type: '—', verdict: 'pick a file first', rebuild_status: '—' }]);
        return;
      }
      for (const f of files) {
        const row = await scanOne(f.name);
        row.mime_type = row.mime_type || f.type || '—';
        scanned.push(row);
      }
      renderRows(scanned);
    });

    printBtn.addEventListener('click', () => {
      window.print(); // TRL-4: paper receipt via PDF receipt (src/audit/receipt_pdf.py)
    });
  });
})();
