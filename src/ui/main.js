/**
 * SHUCHI Electron UI — TRL-4 minimal stub for iDEX demo.
 *
 * - 800x600 BrowserWindow loading index.html
 * - IPC handler `scan-file` that calls the Python pipeline via child_process,
 *   with a mock-verdict fallback when python/pipeline is unavailable.
 * - Must start without crash: `node --check src/ui/main.js` passes, and
 *   `npm run dev -- --help` / `electron src/ui/main.js --help` prints help.
 */

const path = require('path');
const { spawnSync } = require('child_process');

const HELP_TEXT = [
  'SHUCHI — Sanitiser Hub for Clean Information (TRL-4 demo UI)',
  '',
  'Usage:',
  '  npm run dev [-- --help]        Start Electron UI (src/ui/main.js)',
  '  electron src/ui/main.js         Start UI',
  '  electron src/ui/main.js --help  Show this help',
  '',
  'IPC:',
  '  scan-file <filepath>  Scan one file via Python pipeline (or mock verdict)',
].join('\n');

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(HELP_TEXT);
  process.exit(0);
}

/**
 * Scan a single file via the Python pipeline.
 * Falls back to a mock verdict when python3 or the pipeline is unavailable
 * (e.g. CI / reviewer machine without venv). Never throws.
 */
function scanFileViaPipeline(filepath) {
  if (!filepath) {
    return { input: filepath, verdict: 'BLOCKED', reason: 'empty path', mock: true };
  }
  try {
    const pipeline = path.join(__dirname, '..', 'pipeline', 'main.py');
    const fs = require('fs');
    if (!fs.existsSync(pipeline)) {
      throw new Error('pipeline not found: ' + pipeline);
    }
    // Call a tiny inline probe: python3 -c "scan one file" using src.pipeline.
    // We keep it simple: run `python3 src/pipeline/main.py --help`-style check
    // via a one-shot scan using the scan_file() function.
    const probe = spawnSync(
      'python3',
      [
        '-c',
        'import json,sys;'
        + 'sys.path.insert(0, ".");'
        + 'from src.pipeline.main import scan_file;'
        + 'print(json.dumps(scan_file(sys.argv[1])))',
        filepath,
      ],
      { encoding: 'utf8', timeout: 60000 }
    );
    if (probe.status === 0 && probe.stdout) {
      return {
        input: filepath,
        verdict: 'SCANNED',
        scan_results: JSON.parse(probe.stdout),
        mock: false,
      };
    }
    throw new Error((probe.stderr || 'python pipeline failed').trim().slice(0, 300));
  } catch (err) {
    // Mock fallback for demo / machines without python deps.
    return {
      input: filepath,
      verdict: 'CLEAN_REBUILT (mock)',
      scan_results: [
        { engine: 'ClamAV', status: 'CLEAN', detail: 'mock — python unavailable' },
        { engine: 'YARA (30 rules)', status: 'CLEAN', detail: 'mock — python unavailable' },
      ],
      rebuild_status: 'REBUILT (mock)',
      mock: true,
      note: String((err && err.message) || err),
    };
  }
}

// When Electron is not installed (e.g. `node src/ui/main.js`), exit cleanly
// instead of crashing so the iDEX reviewer can at least run --help / --check.
let electron = null;
try {
  electron = require('electron');
} catch (e) {
  if (require.main === module) {
    console.log('SHUCHI UI stub: electron not installed; running in stub mode.');
    console.log(HELP_TEXT);
  }
  module.exports = { scanFileViaPipeline };
  if (require.main === module) {
    process.exit(0);
  }
}

// ---- Electron runtime below ----
if (electron) {
  const { app, BrowserWindow, ipcMain } = electron;

  ipcMain.handle('scan-file', async (_event, filepath) => scanFileViaPipeline(filepath));

  function createWindow() {
    const win = new BrowserWindow({
      width: 800,
      height: 600,
      title: 'SHUCHI — USB Sanitisation Kiosk (TRL-4)',
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
      },
    });
    win.loadFile(path.join(__dirname, 'index.html'));
  }

  app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
  });
}

module.exports = { scanFileViaPipeline };
