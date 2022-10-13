# Pizza redirects
Manage your Pizza Redirects as IaC (Infrastructure as Code) with this simple tool.

## Setup

Create environment and install requirements

```bash
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

Export the following environment variables:
```bash
export PIZZA_TOKEN=...
```

## Usage: 
Pull latest state from redirects.pizza 
```bash
redirects.py pull
```

Push local state to redirects.pizza 
```bash
redirects.py push
```

use `--force` to skip confirmation

use `--dryrun` to skip actual push and local overwrite

## redirects.yaml
All redirects will be stored in redirects.yaml.

Do not set the `id` field on new redirects. It will be pulled automatically from the API after creation.

```yaml
- destination: https://www.example.ch/yourpath
  id: 123456789
  keep_query_string: false
  redirect_type: permanent
  sources:
  - example.ch
  - "*.example.ch"
  - another.domain.ch/yourpath
  tags:
  - mytag
  tracking: true
  uri_forwarding: false
```

## Github Action 
You can use this tool in a Github Action to automatically update your redirects on redirects.pizza.

make sure to set the `PIZZA_TOKEN` environment variable in your Github Action Secrets.

