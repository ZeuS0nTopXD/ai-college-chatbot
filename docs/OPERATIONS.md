# Operations

## Scheduled source refresh

The repository includes a weekly GitHub Actions workflow at
`.github/workflows/refresh-vsit-sources.yml`. Add these repository secrets:

- `VSIT_APP_URL`: the deployed app URL, without a trailing slash
- `VSIT_ADMIN_TOKEN`: an admin bearer token issued by the app

The workflow can also be started manually from the Actions tab. It refreshes
only public VSIT pages and never accesses student records.

## Remaining integrations

Personal marks, attendance, fees, authenticated results, form submission, and
student notifications require an official VSIT portal API or an approved
integration. Do not place student passwords or portal credentials in this
repository or in the public chatbot.
