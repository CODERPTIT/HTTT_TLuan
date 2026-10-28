# Verification artifacts

Run `node tests/browser_smoke.mjs` from the project directory to generate desktop/mobile screenshots and `browser-report.json`.

The script uses an installed Chrome browser and a temporary, isolated SQLite database. It starts and stops its own local Uvicorn and headless Chrome processes. Set `ABC_PYTHON` to the Python interpreter with the project dependencies and `CHROME_PATH` if Chrome is installed elsewhere.

Screenshots are UI verification artifacts, not product source images.

