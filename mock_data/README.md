Mock data for development and demonstrations

Files are generated automatically by the seed utilities. They are stored in this folder by default.

Generated files:
- users.xlsx: demo users (admin, digitador, pesquisador)
- fishermen_mock_data.xlsx: 30+ fictitious socioeconomic submissions

How to (re)generate:

Run the seeding script from the project root:

```bash
python seed.py         # create mock files and populate the SQLite DB
python seed.py --reset # clear existing submissions and repopulate
```

To disable automatic seeding on app startup, set the environment variable `SEED_ON_STARTUP=false`.

Note: The seed is idempotent and will avoid duplicating submissions based on CPF.

All mock records are clearly marked with "Registro gerado automaticamente (mock)" in the `observacoes` field.

Requirements: `pandas` and `openpyxl` must be installed in the project's Python environment.
