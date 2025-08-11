# AWS Infrastructure with Auto-Termination

CloudFormation templates for AWS resources that automatically terminate after a specified time period to prevent runaway costs.

## Templates

### 1. G5 GPU Instance (`g5-instance-cloudformation.yaml`)
GPU-enabled EC2 instances for machine learning and compute workloads.

### 2. Aurora PostgreSQL (`aurora-postgresql-cloudformation.yaml`)
Managed PostgreSQL database cluster with high availability.

## Quick Deploy

### AWS Console
1. CloudFormation → Create Stack → Upload template file
2. Set parameters and deploy with CAPABILITY_IAM

## G5 Instance Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `InstanceType` | `g5.xlarge` | g5.xlarge, g5.2xlarge, g5.4xlarge, etc. |
| `KeyPairName` | `""` | Leave empty for SSM-only access |
| `TerminationHours` | `336` (14 days) | 2=testing, 24=1day, 168=1week |

## Aurora PostgreSQL Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `Region` | `us-east-1` | us-east-1, us-west-2, eu-west-1, ap-southeast-1 (Singapore), ap-east-1 (Hong Kong), etc. |
| `DBInstanceClass` | `db.r6g.large` | db.r6g.large, db.r6g.xlarge, db.r6g.2xlarge, etc. |
| `MasterUsername` | `postgres` | Database master username |
| `MasterUserPassword` | - | Database master password (8-128 chars) |
| `DatabaseName` | `mydb` | Initial database name |
| `TerminationHours` | `336` (14 days) | 2=testing, 24=1day, 168=1week |

## Features

### G5 Instance
- **Auto-termination**: Lambda checks hourly, terminates expired instances
- **Secure**: No ingress rules, SSM access only
- **GPU-ready**: NVIDIA drivers, CUDA, Docker pre-installed
- **Cost-aware**: g5.xlarge ~$1/hr, auto-terminates to prevent runaway costs

### Aurora PostgreSQL
- **Auto-termination**: Lambda checks hourly, deletes expired clusters
- **Secure**: Private subnets, no public access
- **High availability**: Multi-AZ deployment with automated backups
- **Cost-aware**: db.r6g.large ~$0.29/hr, auto-terminates to prevent runaway costs
- **Encrypted**: Storage encryption enabled by default

## Connection Information

### Aurora PostgreSQL
After deployment, use the outputs to connect:
- **Endpoint**: Use `ClusterEndpoint` output
- **Port**: Use `ClusterPort` output (default: 5432)
- **Database**: Use `DatabaseName` parameter value
- **Security**: Attach `ClientSecurityGroupId` to resources that need database access
