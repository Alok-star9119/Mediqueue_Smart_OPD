# MediQueue Project Report

## Abstract
MediQueue is a cloud-computing prototype for managing outpatient department (OPD) appointments and queues. It lets a demo user book a token, check token status, and view a staff summary. The system uses generated synthetic records to avoid using real patient information.

## Problem
Manual OPD queues can create long waits, duplicate records, and limited visibility into demand. MediQueue demonstrates how a web application and central database can provide a simple digital queue.

## Objectives
1. Provide online appointment booking and token generation.
2. Display appointment and queue status.
3. Generate synthetic records for demonstration and testing.
4. package the application as a Docker container.
5. demonstrate deployment concepts with Kubernetes and AWS ECS.
6. expose health endpoints that can support monitoring.

## Technology stack
- Python and FastAPI for REST endpoints.
- SQLAlchemy for database access.
- PostgreSQL for local containerized persistence; SQLite is supported for quick development.
- HTML/CSS/JavaScript for the lightweight web interface.
- Docker Compose for local orchestration.
- Kubernetes YAML for learning deployments.
- Terraform starter for AWS ECS/Fargate.

## Functional modules
- Department and doctor directory
- Appointment booking and token generation
- Queue lookup and estimated wait (demo assumption: eight minutes per waiting token ahead)
- Staff summary
- Appointment status update
- Health/readiness checks
- Synthetic data seeding

## Synthetic data
The seed module creates fictional department and doctor names, sample patient names, and contacts ending in `example.test`. These records are generated only for the demo and are not intended to represent real people.

## Cloud design
The application runs in a stateless container. Persistent data is externalized to PostgreSQL in Docker Compose. The Kubernetes files illustrate Deployment, Service, ConfigMap, and a demo-only PostgreSQL deployment. The Terraform starter creates an ECS/Fargate service behind an Application Load Balancer and an ECR repository. For a production-like cloud design, use RDS PostgreSQL in private subnets, Secrets Manager, TLS, monitoring alarms, backups, and access controls.

## Reliability targets
The source project idea lists targets of 99.9% availability, P95 response under two seconds, RTO 15 minutes, RPO five minutes, and critical TTR five minutes. This implementation does not claim these targets are achieved. They must be measured with repeatable load and failure tests.

## Limitations
- Demo staff endpoints have no authentication or authorization.
- The estimate of eight minutes per person ahead is a fixed demonstration assumption.
- SQLite is not suitable for horizontally scaled production instances.
- Kubernetes Postgres manifest uses demo credentials and has no persistent volume.
- AWS Terraform starter uses SQLite and HTTP for a low-friction demo; it is not production-ready.
- No real SMS, email reminders, hospital integration, or clinical decision-making is implemented.

## Future improvements
- Add login and role-based access control.
- Use RDS PostgreSQL, private networking, TLS, Secrets Manager, and encrypted backups.
- Add Alembic migrations and audit logging.
- Add CloudWatch metrics, alarms, tracing, and notification delivery.
- Use k6/JMeter to measure throughput, P95/P99 latency, availability, and recovery time.
- Add CI/CD and infrastructure testing.
