# Infrastructure

Local infrastructure configuration for Vortex SICM.

`docker-compose.yml` contains the repository's local container orchestration configuration. Deployment configuration for the frontend is maintained at the repository level in `vercel.json` and in the deployment platform settings.

Keep infrastructure minimal and aligned with the actual application dependencies. Do not add services that are not required by the running system.