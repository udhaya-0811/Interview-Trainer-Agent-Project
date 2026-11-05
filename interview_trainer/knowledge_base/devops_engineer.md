# DevOps Engineer Interview Knowledge Base
# Role: DevOps Engineer | Category: Technical

---
## Q1 | difficulty: beginner
**Question:** What is DevOps and what are its core principles?

**Answer:**
DevOps is a cultural and engineering practice that unifies software development (Dev) and IT operations (Ops) to shorten the development lifecycle and deliver high-quality software continuously.
Core principles:
- **Culture of collaboration:** break down silos between Dev, QA, and Ops.
- **CI/CD:** automate build, test, and deployment pipelines.
- **Infrastructure as Code (IaC):** manage infrastructure with code (versioned, reviewed, automated).
- **Monitoring and observability:** measure everything; feedback loops inform improvement.
- **Fail fast:** detect and fix problems early in the pipeline; embrace blameless post-mortems.
The CALMS framework: Culture, Automation, Lean, Measurement, Sharing.

---
## Q2 | difficulty: intermediate
**Question:** What is CI/CD? Describe a typical pipeline.

**Answer:**
**CI (Continuous Integration):** automatically build and test code on every commit. Catches integration issues early.
**CD (Continuous Delivery):** automatically deploy to staging after CI; production deployment requires manual approval.
**Continuous Deployment:** fully automated deployment to production on every green build.
Typical pipeline stages:
1. Source trigger (push/PR to main)
2. Code checkout
3. Dependency installation
4. Static analysis (lint, SAST security scan)
5. Unit tests + coverage gate
6. Build (Docker image, JAR, etc.)
7. Integration tests
8. Push artifact to registry
9. Deploy to staging
10. Smoke tests / E2E tests
11. Deploy to production (blue-green or canary)
12. Monitor and alert
Tools: GitHub Actions, GitLab CI, Jenkins, CircleCI, ArgoCD (GitOps).

---
## Q3 | difficulty: intermediate
**Question:** What is Docker? Explain key concepts: image, container, Dockerfile, registry.

**Answer:**
Docker packages applications and dependencies into containers — isolated, portable, reproducible runtime environments.
- **Image:** read-only template built from a Dockerfile. Layered (each instruction = layer; cached for speed).
- **Container:** running instance of an image. Isolated process with its own filesystem, network, process space.
- **Dockerfile:** text file with instructions to build an image (FROM, RUN, COPY, ENV, EXPOSE, CMD, ENTRYPOINT).
- **Registry:** stores and distributes images. Docker Hub (public), AWS ECR, Google GCR, GitHub Container Registry (private).
Multi-stage builds reduce image size by separating build environment from runtime.
Best practices: use official base images, run as non-root, scan images for vulnerabilities (`docker scout`), minimise layers.

---
## Q4 | difficulty: advanced
**Question:** What is Kubernetes? Explain core objects: Pod, Deployment, Service, Ingress.

**Answer:**
Kubernetes (K8s) is a container orchestration platform that automates deployment, scaling, and management of containerised applications.
Core objects:
- **Pod:** smallest deployable unit; one or more containers sharing network/storage. Ephemeral — don't persist state.
- **Deployment:** declares desired state (replicas, image version); manages rolling updates and rollbacks.
- **Service:** stable network endpoint (ClusterIP, NodePort, LoadBalancer) that load-balances across Pod replicas. Decouples consumers from Pod churn.
- **Ingress:** HTTP/S routing rules; terminates TLS; routes traffic to Services based on host/path. Requires an Ingress Controller (nginx, Traefik).
- **ConfigMap / Secret:** externalise configuration and credentials from container images.
- **HorizontalPodAutoscaler (HPA):** automatically scale Deployments based on CPU/memory or custom metrics.

---
## Q5 | difficulty: advanced
**Question:** What is Infrastructure as Code (IaC)? Terraform vs Ansible?

**Answer:**
IaC manages infrastructure (cloud resources, network, servers) via machine-readable definition files — enabling versioning, review, and automation.
**Terraform (HashiCorp):** declarative, cloud-agnostic provisioning. Defines desired state; applies changes to reach it. State file tracks real infrastructure. Plan → Apply workflow enables safe changes.
**Ansible:** agentless, procedural configuration management. SSH-based, executes playbooks (YAML) on existing servers. Better for configuring OS, installing packages, deploying apps to existing VMs.
**When to use:** Terraform for provisioning cloud infrastructure (VPCs, EC2, RDS, EKS); Ansible for configuring servers and deploying applications. Often used together.
Other IaC tools: AWS CloudFormation, Pulumi (code-based IaC), CDK.

---
## Q6 | difficulty: intermediate
**Question:** What is the difference between blue-green deployment and canary deployment?

**Answer:**
Both are zero-downtime deployment strategies.
**Blue-Green:** maintain two identical environments (blue=current, green=new). Deploy to green, test, then switch all traffic. Easy rollback (switch back to blue). Double infrastructure cost during switch.
**Canary:** gradually roll out new version to a small percentage of traffic (5% → 25% → 100%). Monitor metrics at each stage; abort if errors spike. Slower but lower risk and resource cost.
**Rolling update (K8s default):** replace Pods one-by-one. Gradual rollout; brief period with mixed versions. Low cost; no instant rollback.
**Feature flags:** deploy code to all users but control activation per user segment. Decouple deployment from release.

---
## Q7 | difficulty: intermediate
**Question:** What is observability? Explain the three pillars: logs, metrics, traces.

**Answer:**
Observability is the ability to understand the internal state of a system from its external outputs.
Three pillars:
- **Logs:** immutable, timestamped records of events. Use structured logging (JSON) for machine parseability. Tools: ELK Stack (Elasticsearch, Logstash, Kibana), Loki + Grafana.
- **Metrics:** numerical measurements over time (request rate, error rate, latency, CPU). Time-series data aggregated into dashboards and alerts. Tools: Prometheus + Grafana.
- **Distributed traces:** track a request across services with trace IDs and spans. Identify latency bottlenecks across microservices. Tools: Jaeger, Zipkin, Datadog APM, AWS X-Ray.
SRE golden signals: Latency, Traffic, Errors, Saturation (LTES). SLOs (Service Level Objectives) + SLAs + error budgets govern production reliability.

---
## Q8 | difficulty: advanced
**Question:** What is GitOps and how does ArgoCD implement it?

**Answer:**
GitOps is a deployment model where Git is the single source of truth for infrastructure and application state. All changes go through Git (PR, review, merge); automation applies them.
**ArgoCD** is a declarative, GitOps-based continuous delivery tool for Kubernetes:
1. Git repo contains K8s manifests (or Helm charts, Kustomize).
2. ArgoCD continuously watches the repo and the cluster.
3. On divergence (drift), ArgoCD can auto-sync or alert.
4. Rollback = `git revert`; audit trail = git history.
Benefits: declarative, auditable, self-healing, no direct `kubectl` in production.
Flow: Developer pushes code → CI pipeline → builds image, updates image tag in config repo → ArgoCD detects change → applies to cluster.

---
## Q9 | difficulty: intermediate
**Question:** What is a service mesh? What does Istio provide?

**Answer:**
A service mesh is a dedicated infrastructure layer for service-to-service communication, handling cross-cutting concerns without modifying application code.
**Istio** is the most popular service mesh:
- **Traffic management:** fine-grained routing (canary, A/B), retries, timeouts, circuit breaking via VirtualService and DestinationRule.
- **Security (mTLS):** automatic mutual TLS between services; zero-trust networking.
- **Observability:** automatic metrics, logs, and traces for every service call without code changes (Envoy sidecar proxy).
- **Policy enforcement:** rate limiting, RBAC.
Architecture: Envoy sidecar proxies (data plane) + Istiod control plane.
Trade-offs: adds latency (proxy hops), operational complexity, and resource overhead. Justified for large microservices deployments needing security and observability.

---
## Q10 | difficulty: advanced
**Question:** How do you manage secrets in a production Kubernetes environment?

**Answer:**
Kubernetes Secrets are base64-encoded (not encrypted) by default — not secure enough for production.
Production approaches:
1. **Encryption at rest:** enable `EncryptionConfiguration` in the API server with a KMS provider (AWS KMS, GCP KMS).
2. **External Secrets Operator:** syncs secrets from external vaults (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) into K8s Secrets. Source of truth stays outside the cluster.
3. **HashiCorp Vault:** enterprise secret management; dynamic secrets (short-lived DB credentials), secret leasing, audit logs. Integrated with K8s via Vault Agent Injector.
4. **Sealed Secrets (Bitnami):** encrypt secrets client-side; only the cluster's controller can decrypt. Safe to store encrypted Sealed Secrets in Git (GitOps-compatible).
Never commit plain secrets to Git. Rotate secrets regularly. Use RBAC to restrict Secret access.

---
## Q11 | difficulty: intermediate
**Question:** What is Helm in Kubernetes?

**Answer:**
Helm is the package manager for Kubernetes. It bundles K8s manifests into reusable, parameterisable packages called **charts**.
- **Chart:** directory with templates (YAML with Go templating), `values.yaml` (default config), `Chart.yaml` (metadata).
- **Release:** deployed instance of a chart with specific values.
- **Repository:** index of charts (Artifact Hub, Bitnami, custom).
Benefits: reuse community charts (nginx, cert-manager, Redis), parameterise deployments for different environments (dev/staging/prod), version-controlled releases, easy upgrades and rollbacks (`helm upgrade`, `helm rollback`).
`helm template` renders manifests locally for debugging without installing. `helmfile` manages multiple charts declaratively.

---
## Q12 | difficulty: advanced
**Question:** What is chaos engineering? How do you practise it?

**Answer:**
Chaos engineering is the discipline of experimenting on production systems to build confidence in their ability to withstand turbulent conditions.
Principles (Netflix Chaos Monkey origin):
1. Define steady state (normal behaviour measurable by SLOs).
2. Hypothesise: "steady state will hold even when X fails."
3. Introduce realistic failure: kill pods, inject latency, simulate network partition, drain a node.
4. Observe: does the system recover? Are alerts triggered? Is the user impact acceptable?
5. Fix weaknesses discovered.
Tools: Chaos Monkey, Gremlin (SaaS), LitmusChaos (CNCF, K8s-native), AWS Fault Injection Simulator.
Start in staging, not production. Gradually expand blast radius. Always have a kill switch. Document findings in runbooks.

---
## Q13 | difficulty: intermediate
**Question:** What are Linux commands every DevOps engineer should know?

**Answer:**
File and navigation: `ls -lah`, `find`, `locate`, `tree`, `du -sh`
Text processing: `grep -r`, `awk`, `sed`, `cut`, `sort`, `uniq`, `wc -l`, `tail -f`, `head`
Process management: `ps aux`, `top`/`htop`, `kill`/`pkill`, `lsof`, `strace`
Network: `netstat -tulnp`, `ss -tulnp`, `curl`, `wget`, `ping`, `traceroute`, `nmap`, `tcpdump`
System: `df -h`, `free -m`, `vmstat`, `iostat`, `dmesg`, `journalctl`
Permissions: `chmod`, `chown`, `umask`, `sudo`, `visudo`
Archives: `tar -xzvf`, `gzip`, `zip`
Useful combos: `netstat -tulnp | grep :8080` — what's listening on port 8080; `ps aux | grep java | awk '{print $2}'` — get PID of java process.

---
## Q14 | difficulty: advanced
**Question:** What is AWS and what are its core services for a cloud-native application?

**Answer:**
Core AWS services:
- **Compute:** EC2 (VMs), ECS (containers), EKS (Kubernetes), Lambda (serverless).
- **Storage:** S3 (object), EBS (block, EC2 volumes), EFS (NFS, shared), Glacier (archival).
- **Database:** RDS (managed relational — MySQL/Postgres/Aurora), DynamoDB (NoSQL), ElastiCache (Redis/Memcached), Redshift (data warehouse).
- **Networking:** VPC, Route53 (DNS), CloudFront (CDN), ALB/NLB (load balancers), API Gateway.
- **CI/CD:** CodePipeline, CodeBuild, CodeDeploy; or GitHub Actions deploying to AWS.
- **Secrets & Config:** Secrets Manager, Parameter Store.
- **Observability:** CloudWatch (logs, metrics, alarms), X-Ray (tracing), CloudTrail (audit).
- **Security:** IAM (identity), Security Groups (firewall), WAF, KMS (key management), GuardDuty (threat detection).

---
## Q15 | difficulty: intermediate
**Question:** What is a VPC (Virtual Private Cloud) and how do you design one for security?

**Answer:**
A VPC is an isolated virtual network in AWS (or GCP/Azure equivalent) where you control IP ranges, subnets, routing, and internet access.
Secure VPC design:
- **Public subnets:** internet-facing resources (ALB, NAT Gateway, bastion host). Route to Internet Gateway.
- **Private subnets:** application layer (EC2, ECS, EKS). No direct internet access; outbound via NAT Gateway.
- **Database subnets:** no internet access at all; accessible only from app subnets via Security Groups.
- **Security Groups:** stateful firewall at instance/service level. Allow only required ports from required sources.
- **NACLs:** stateless subnet-level firewall. Additional defence-in-depth layer.
- **VPC Flow Logs:** capture network traffic for security analysis.
- **PrivateLink:** access AWS services privately without traversing the internet.

---
## Q16 | difficulty: advanced
**Question:** What is SRE (Site Reliability Engineering)? How does it differ from DevOps?

**Answer:**
SRE (Google's model) applies software engineering principles to operations. Key concepts:
- **SLI (Service Level Indicator):** measurable metric (request success rate, latency p99).
- **SLO (Service Level Objective):** target for an SLI (99.9% success rate). Internal commitment.
- **SLA (Service Level Agreement):** external contractual commitment. SLA ≤ SLO (buffer for buffer).
- **Error budget:** 1 - SLO. Team "spends" it on risk (new features, experiments); when exhausted, focus on reliability.
- **Toil:** repetitive, manual operational work. SRE goal: reduce toil via automation below 50% of time.
DevOps vs SRE: DevOps is a culture/philosophy; SRE is an opinionated implementation. SRE formalises reliability targets; DevOps is broader about collaboration and velocity.

---
## Q17 | difficulty: intermediate
**Question:** What is container security? Best practices for securing Docker containers?

**Answer:**
Container security layers:
1. **Base image:** use minimal, official images (Alpine, distroless). Regularly scan with Trivy, Snyk, Docker Scout.
2. **Non-root user:** `RUN addgroup -S app && adduser -S app -G app; USER app`.
3. **Read-only filesystem:** `--read-only` flag; explicit volumes for writable paths.
4. **No secrets in images:** use environment variables or secret managers, not COPY of .env files.
5. **Drop capabilities:** `--cap-drop ALL --cap-add NET_BIND_SERVICE` (principle of least privilege).
6. **Resource limits:** `--memory 512m --cpus 0.5` to prevent resource exhaustion.
7. **Network policies:** K8s NetworkPolicy to restrict pod-to-pod communication.
8. **Image signing:** Cosign / Notary; admission controllers verify image provenance.
9. **Supply chain security:** pin digest (`FROM nginx@sha256:...`), SBOM generation.

---
## Q18 | difficulty: advanced
**Question:** How does auto-scaling work in Kubernetes and AWS?

**Answer:**
**Kubernetes scaling:**
- **HPA (Horizontal Pod Autoscaler):** scales Deployment replicas based on CPU/memory or custom metrics (Prometheus Adapter, KEDA for event-driven scaling).
- **VPA (Vertical Pod Autoscaler):** adjusts resource requests/limits per pod. Not as commonly used in production (requires pod restarts).
- **KEDA (Kubernetes Event-Driven Autoscaling):** scale to zero and scale based on queue depth, Kafka lag, etc.
**Cluster scaling:**
- **Cluster Autoscaler:** adds/removes EC2 nodes when pods are pending or nodes are underutilised.
- **Karpenter (AWS):** modern, faster node provisioning; can right-size instance types based on pod requirements.
**AWS Auto Scaling Groups (ASG):** scale EC2 instances; policies: step scaling, target tracking (e.g., keep CPU at 50%), scheduled.

---
## Q19 | difficulty: intermediate
**Question:** What is a load balancer? Layer 4 vs Layer 7?

**Answer:**
A load balancer distributes traffic across multiple backend instances for scalability, availability, and fault tolerance.
**Layer 4 (Transport layer):** routes based on IP and TCP/UDP port. Faster, no content inspection. AWS NLB (Network Load Balancer). Use for: TCP, TLS passthrough, extremely high throughput, UDP protocols.
**Layer 7 (Application layer):** routes based on HTTP headers, URL, hostname, cookies. Can terminate TLS, inspect and rewrite requests, sticky sessions. AWS ALB (Application Load Balancer). Use for: HTTP microservices, path-based routing (`/api` → API service, `/` → frontend), WebSocket support, gRPC.
**Algorithms:** round-robin, least connections, IP hash (sticky), weighted round-robin.

---
## Q20 | difficulty: advanced
**Question:** What is the 12-factor app methodology?

**Answer:**
12-factor is a methodology for building portable, scalable, cloud-native applications:
1. **Codebase:** one codebase, many deployments.
2. **Dependencies:** explicitly declare and isolate dependencies (requirements.txt, package.json).
3. **Config:** store config in environment variables (not code).
4. **Backing services:** treat databases, queues, caches as attached resources (URL in config).
5. **Build, release, run:** strictly separate build → release → run stages.
6. **Processes:** stateless processes; store state in backing services.
7. **Port binding:** export services via port binding (HTTP server as process, not servlet).
8. **Concurrency:** scale out via process model (horizontal scaling).
9. **Disposability:** fast startup, graceful shutdown (SIGTERM handling).
10. **Dev/prod parity:** keep environments similar (same DB, same versions).
11. **Logs:** treat logs as event streams (stdout → log aggregator).
12. **Admin processes:** run admin tasks as one-off processes in same environment.

---
## Q21 | difficulty: intermediate
**Question:** What is PostgreSQL and what are common performance tuning techniques?

**Answer:**
PostgreSQL is an open-source, ACID-compliant relational database.
Performance tuning:
- **Indexes:** B-tree (default), GiST (geometric), GIN (full-text), partial indexes (`WHERE` condition), expression indexes.
- **EXPLAIN ANALYZE:** understand query plan; look for Seq Scan on large tables, hash joins vs nested loops.
- **Connection pooling:** PgBouncer reduces connection overhead (PostgreSQL creates a process per connection).
- **Vacuum and Analyze:** autovacuum cleans dead tuples; `ANALYZE` updates statistics.
- **Work_mem:** increase for sort/hash operations on large datasets (`SET work_mem = '64MB'`).
- **Partitioning:** declarative partitioning by range/list for large tables.
- **Read replicas:** offload reporting queries from primary.
- **Caching:** `shared_buffers` (25% of RAM), `effective_cache_size`.

---
## Q22 | difficulty: intermediate
**Question:** What is Redis and what are common use cases?

**Answer:**
Redis is an in-memory data structure store used as cache, message broker, and database.
Data structures: String, List, Hash, Set, Sorted Set (ZSet), HyperLogLog, Streams, Pub/Sub.
Common use cases:
- **Caching:** store DB query results, session data, API responses with TTL (`SETEX key 3600 value`).
- **Rate limiting:** INCR + EXPIRE for fixed-window; sorted sets for sliding-window counters.
- **Session store:** distributed sessions across multiple app instances.
- **Pub/Sub:** lightweight message broker for real-time notifications.
- **Distributed locks:** `SET lock NX PX 30000` (Redlock algorithm for distributed systems).
- **Leaderboards:** Sorted Sets for real-time rankings.
Persistence: RDB (snapshots) vs AOF (append-only log) for durability. Redis Cluster for horizontal sharding.

---
## Q23 | difficulty: advanced
**Question:** What is the difference between stateful and stateless applications? How do you handle stateful workloads in Kubernetes?

**Answer:**
- **Stateless:** each request is independent; no local persistent data. Easy to scale horizontally; any replica handles any request. Examples: REST APIs, static servers.
- **Stateful:** maintains data or connection state across requests. Cannot be arbitrarily replaced. Examples: databases, message queues, ML inference services with loaded models.
**Kubernetes for stateful workloads:**
- **StatefulSet:** ordered Pod deployment/scaling; stable network identity (`pod-0`, `pod-1`); stable persistent storage via PVCs.
- **PersistentVolume (PV) / PersistentVolumeClaim (PVC):** abstract storage; PV is the actual storage resource; PVC is the claim by a Pod.
- **Headless Service** (`clusterIP: None`): direct DNS to individual Pods by name (needed for database clustering).
- **Operators:** custom controllers managing complex stateful applications (PostgreSQL Operator, Kafka Operator, Redis Operator) with domain-specific operational knowledge.

---
## Q24 | difficulty: beginner
**Question:** What is version control with Git? Explain branching strategies.

**Answer:**
Git tracks changes to code enabling collaboration and history.
Core concepts: repository, commit, branch, merge, rebase, remote (origin), push, pull.
Branching strategies:
- **Git Flow:** `main` (production), `develop` (integration), `feature/*`, `release/*`, `hotfix/*`. Structured but complex.
- **GitHub Flow:** `main` + short-lived `feature/*` branches. Simple, suitable for continuous deployment.
- **Trunk-based development:** all developers commit to main (trunk) at least daily via short-lived feature branches or feature flags. Enables true CI; preferred in high-performing DevOps teams.
PR best practices: small, focused PRs; descriptive commit messages (Conventional Commits format); require CI to pass before merge.

---
## Q25 | difficulty: advanced
**Question:** How do you debug a production incident? Walk through your process.

**Answer:**
Incident response process:
1. **Detect:** alert fires (PagerDuty/Opsgenie), users report, dashboard spike.
2. **Triage severity:** P1 (major outage) vs P2 (degraded) — drives urgency and who to involve.
3. **Communicate:** post in incident channel, notify stakeholders, set expectations for update frequency.
4. **Gather data:** check metrics (request rate, error rate, latency, CPU/memory), recent deployments (`kubectl rollout history`, recent PRs), logs (`kubectl logs`, Loki/ELK), traces.
5. **Hypothesise and isolate:** form hypotheses, test one at a time. Don't change multiple things simultaneously.
6. **Mitigate:** rollback deployment, scale up, disable feature flag — fastest path to user impact reduction.
7. **Root cause analysis:** with timeline restored, deep-dive what caused the issue.
8. **Post-mortem:** blameless; timeline, root cause, contributing factors, action items with owners and dates.
