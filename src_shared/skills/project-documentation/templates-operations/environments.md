# Environments

## Environment Matrix

| Environment | Purpose | URL | Region | Infra | Auto-Deploy | Refresh Schedule |
|------------|---------|-----|--------|-------|-------------|-----------------|
| Development | {local dev / shared dev} | {url} | {region} | {type} | {Yes/No} | {N/A} |
| Staging | {pre-prod validation} | {url} | {region} | {type} | {Yes/No} | {frequency} |
| Production | {live traffic} | {url} | {region} | {type} | {No} | {N/A} |

## Environment Details

### Production

**Infrastructure**:
- **Compute**: {Cloud Run / ECS / EC2 / K8s / etc.} — {instance type, replicas}
- **Database**: {service} — {instance type, version, storage}
- **Cache**: {service} — {instance type, size}
- **Storage**: {S3/GCS/Azure Blob} — {bucket names, region}
- **CDN**: {service} — {distribution ID}
- **DNS**: {provider} — {domain management}

**Network**:
- **VPC/VNet**: {name, CIDR}
- **Subnets**: {public/private layout}
- **Security Groups / Firewall Rules**: {key rules}
- **WAF**: {provider, rule sets}

**Access**:
- **Cloud Console**: {URL, required IAM role}
- **CLI Access**: {tool, profile/project name}
- **SSH/Bastion**: {how to connect}
- **Database Direct**: {connection method, tunnel required?}

### Staging

{Same structure as Production — document differences.}

### Development

{Same structure — document differences.}

## Environment Parity

| Aspect | Dev | Staging | Prod | Notes |
|--------|-----|---------|------|-------|
| Database engine | {same?} | {same?} | {PostgreSQL 15} | |
| Data volume | {synthetic} | {subset of prod} | {full} | {how staging data refreshed} |
| External services | {mocked?} | {sandbox?} | {live} | |
| Auth provider | {local?} | {staging instance} | {prod instance} | |
| Feature flags | {all on} | {mirrors prod} | {controlled} | |

## Cloud Project / Account Mapping

| Cloud Provider | Account/Project | Environment | Owner |
|---------------|----------------|-------------|-------|
| {GCP/AWS/Azure} | {project-id / account-id} | {Prod/Staging/Dev} | {team} |

## Related Documentation

- [Operations Overview](overview.md) — System inventory
- [Deployment Runbook](runbooks/deployment.md) — How to deploy to each environment
- [Networking & Security](runbooks/networking-security.md) — Network configuration procedures
