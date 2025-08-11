# G5 GPU Instance with Auto-Termination

CloudFormation template for AWS G5 GPU instances that automatically terminate after a specified time period.

## Quick Deploy

### AWS Console
1. CloudFormation → Create Stack → Upload `g5-instance-cloudformation.yaml`
2. Set parameters and deploy with CAPABILITY_IAM

## Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `InstanceType` | `g5.xlarge` | g5.xlarge, g5.2xlarge, g5.4xlarge, etc. |
| `KeyPairName` | `""` | Leave empty for SSM-only access |
| `TerminationHours` | `336` (14 days) | 2=testing, 24=1day, 168=1week |

## Features

- **Auto-termination**: Lambda checks hourly, terminates expired instances
- **Secure**: No ingress rules, SSM access only
- **GPU-ready**: NVIDIA drivers, CUDA, Docker pre-installed
- **Cost-aware**: g5.xlarge ~$1/hr, auto-terminates to prevent runaway costs
