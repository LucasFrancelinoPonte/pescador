# Google Sheets Integration

## Overview

The application can use Google Sheets as a live source for users and as a synchronization target for submitted forms.

### Features

- Load login users from a Google Sheets worksheet.
- Cache sheet data locally as JSON files for offline fallback.
- Append submitted forms to a Google Sheets worksheet.
- Export query results to Google Sheets.
- Synchronize the local cache on startup when enabled.

## Environment Variables

- `GOOGLE_SHEETS_ENABLED=true` to enable the integration.
- `GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json`.
- `GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id`.
- `GOOGLE_SHEETS_USERS_WORKSHEET=Usuarios`.
- `GOOGLE_SHEETS_SUBMISSIONS_WORKSHEET=Formularios`.
- `GOOGLE_SHEETS_EXPORT_WORKSHEET=Exportacao`.
- `GOOGLE_SHEETS_CACHE_DIR=cache/google_sheets`.
- `GOOGLE_SHEETS_SYNC_ON_STARTUP=true`.

## Google Cloud Setup

1. Create a Google Cloud project.
2. Enable the Google Sheets API.
3. Create a service account and download the JSON key file.
4. Share the target spreadsheet with the service account email.
5. Copy the JSON file to a secure location and point `GOOGLE_SERVICE_ACCOUNT_FILE` to it.

## Local Cache

When Google Sheets is unavailable, the application falls back to JSON cache files under `GOOGLE_SHEETS_CACHE_DIR`.

## Sync Behavior

- Users are refreshed from Google Sheets on startup when sync is enabled.
- New form submissions are appended to the submissions worksheet.
- Excel export results can also be pushed to the export worksheet.
