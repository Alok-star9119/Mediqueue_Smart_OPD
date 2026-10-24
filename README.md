# MediQueue — Smart OPD Queue & Appointment System

A runnable educational prototype inspired by the MediQueue Cloud Computing mini-project. It uses **synthetic data only**, FastAPI, PostgreSQL, Docker Compose, Kubernetes manifests, and an AWS ECS/Fargate Terraform starter.

> **Important:** This is a student/demo application, not a production healthcare system. Do not enter real patient data. The SLA figures in the accompanying project idea are targets, not measured results.

## Features
- Browse synthetic departments and doctors
- Book an OPD appointment and receive a token
- View queue status and estimated wait
- Staff dashboard: today's appointments, queue counts, and synthetic summary metrics
- Update appointment status (`waiting`, `in_consultation`, `completed`, `cancelled`)
- Health/readiness endpoints
- Synthetic data seeding
- Automated API tests
- Docker Compose local environment
- Kubernetes Deployment/Service/ConfigMap/Secret examples
- AWS ECS/Fargate + ECR Terraform starter (costs may apply)

## Architecture
Browser → FastAPI web/API container → PostgreSQL  
Local: Docker Compose. Kubernetes: manifests in `k8s/`. AWS: Terraform starter in `infra/aws-ecs/`.

## Run locally (Docker)
Requirements: Docker Engine and Docker Compose plugin.

```bash
cp .env.example .env
docker compose up --build
```
Open http://localhost:8000. API docs: http://localhost:8000/docs. Health: http://localhost:8000/health.

The API container waits for PostgreSQL and creates tables on startup. Seed data is loaded automatically when the database is empty. To reset all demo data:

```bash
docker compose down -v
docker compose up --build
```

## Run without Docker
Requires Python 3.11+ and PostgreSQL. Set `DATABASE_URL`, then:

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

For a quick local-only SQLite run, set `DATABASE_URL=sqlite:///./mediqueue.db` in `.env`. SQLite is for development only.

## API quick reference
- `GET /api/departments`
- `GET /api/doctors?department_id=1`
- `POST /api/appointments` — book appointment
- `GET /api/appointments/{appointment_id}`
- `GET /api/queue?department_id=1`
- `GET /api/staff/summary`
- `PATCH /api/appointments/{appointment_id}/status`
- `GET /health`, `GET /ready`

Example booking:
```bash
curl -X POST http://localhost:8000/api/appointments \\
  -H 'Content-Type: application/json' \\
  -d '{"patient_name":"Demo Patient","patient_contact":"demo@example.test","department_id":1,"doctor_id":1,"appointment_date":"2026-11-01"}'
```
Use a future date for your own demo. The UI automatically defaults to a future date.

## Synthetic data
`app/seed.py` generates fake departments, doctors, and appointment records using deterministic fictional names and `example.test` contact values. You can regenerate sample data:

```bash
python -m app.seed
```
Never use real patient records for this project.

## Tests
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Docker image
```bash
docker build -t mediqueue-api:1.0 .
docker run --rm -p 8000:8000 -e DATABASE_URL=sqlite:///./mediqueue.db mediqueue-api:1.0
```

## Kubernetes (local cluster)
A local cluster such as Minikube or kind is recommended for learning.

1. Build image and make it available to your cluster.
2. Create a namespace and apply manifests:
```bash
kubectl apply -f k8s/
kubectl -n mediqueue get pods,svc
kubectl -n mediqueue port-forward svc/mediqueue 8000:80
```
The Kubernetes example expects a PostgreSQL service named `postgres` and is intended as a learning manifest. For a real cluster, use a managed database, proper Secret management, TLS ingress, resource sizing, and backups. The provided Postgres manifest is a demo only.

## AWS deployment starter
`infra/aws-ecs/` contains Terraform for an ECR repository, ECS cluster, Fargate service, task definition, and public load balancer. Review and configure it before applying. The starter uses a container image URI supplied through a variable; it does not automatically create a managed PostgreSQL database. For a real AWS deployment, add RDS PostgreSQL in private subnets, Secrets Manager, TLS/domain configuration, alarms, backups, and restricted security groups.

```bash
cd infra/aws-ecs
terraform init
terraform plan -var='image_uri=YOUR_ECR_IMAGE_URI'
terraform apply -var='image_uri=YOUR_ECR_IMAGE_URI'
```
AWS resources can incur charges. Destroy the test stack when finished:
```bash
terraform destroy -var='image_uri=YOUR_ECR_IMAGE_URI'
```

## SLA, monitoring and limitations
The reference idea defines targets of 99.9% availability, P95 latency under 2 seconds, RTO 15 minutes, RPO 5 minutes, and a 5-minute critical TTR. These are **design targets only** until you run and document load/failure tests. The prototype does not claim those targets are met. For an academic demo, use k6/JMeter, capture actual latency/throughput, and measure recovery time after stopping the API container.

## Security checklist before production
- Replace demo authentication with verified identity and role-based access control.
- Do not expose staff endpoints publicly without authorization.
- Use TLS, private database networking, managed secrets, encryption, backups, audit logs, and rate limiting.
- Validate privacy/legal requirements and obtain a security review.
- Add migrations (Alembic), observability, CI/CD, and disaster recovery.
