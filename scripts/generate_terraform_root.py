#!/usr/bin/env python3
"""Generate a Terraform root configuration from an approved module contract."""
import json
import os
import re
import urllib.request
from pathlib import Path

OWNER = "aldo2510"
MODULE_REPO = "platform-terraform-modules"
MODULE_ID = os.environ["MODULE_ID"]
INPUTS = json.loads(os.environ["MODULE_INPUTS_JSON"])
ALLOWED = {
    "azure-storage-account": "modules/azure-storage-account/module.yaml",
    "azure-container-apps": "modules/azure-container-apps/module.yaml",
}
if MODULE_ID not in ALLOWED:
    raise SystemExit(f"Module not allowlisted: {MODULE_ID}")

raw_url = f"https://raw.githubusercontent.com/{OWNER}/{MODULE_REPO}/main/{ALLOWED[MODULE_ID]}"
with urllib.request.urlopen(raw_url, timeout=20) as response:
    contract_text = response.read().decode("utf-8")

import yaml
contract = yaml.safe_load(contract_text)
if contract.get("status") != "approved" or contract.get("id") != MODULE_ID:
    raise SystemExit("Module contract is not approved or ID does not match")

schema = {item["name"]: item for item in contract.get("inputs", [])}
unknown = set(INPUTS) - set(schema)
if unknown:
    raise SystemExit(f"Unsupported module input(s): {', '.join(sorted(unknown))}")

def tf_literal(value):
    return json.dumps(value, ensure_ascii=False)

def hcl_type(item):
    return {"string": "string", "number": "number", "boolean": "bool"}.get(item.get("type", "string"), "string")

for name, spec in schema.items():
    if spec.get("required") and name not in INPUTS and "default" not in spec and not spec.get("sensitive"):
        raise SystemExit(f"Missing required input: {name}")
    if name in INPUTS:
        value = INPUTS[name]
        if spec.get("enum") and value not in spec["enum"]:
            raise SystemExit(f"Invalid value for {name}; allowed: {spec['enum']}")
        if spec.get("pattern") and not re.fullmatch(spec["pattern"], str(value)):
            raise SystemExit(f"Value for {name} does not match required pattern")
        if spec.get("type") == "number" and not isinstance(value, (int, float)):
            raise SystemExit(f"Input {name} must be numeric")
        if spec.get("type", "string") == "string" and not isinstance(value, str):
            raise SystemExit(f"Input {name} must be a string")

out = Path("generated-infra")
(out / "terraform").mkdir(parents=True, exist_ok=True)
tfdir = out / "terraform"

variables = []
module_args = []
tfvars = {}
if "subscription_id" not in schema:
    variables.append('variable "subscription_id" {\n  type = string\n  sensitive = true\n}\n')

for name, spec in schema.items():
    typ = hcl_type(spec)
    variables.append(f'variable "{name}" {{\n  type = {typ}')
    if spec.get("sensitive"):
        variables.append("  sensitive = true")
    if "default" in spec and not spec.get("required"):
        variables.append(f"  default = {tf_literal(spec['default'])}")
    variables.append("}\n")
    module_args.append(f"  {name} = var.{name}")
    if name in INPUTS:
        tfvars[name] = INPUTS[name]
    elif "default" in spec:
        tfvars[name] = spec["default"]

main = f'''terraform {{
  required_version = ">= 1.6.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }}
  }}
  backend "azurerm" {{}}
}}

provider "azurerm" {{
  features {{}}
  subscription_id = var.subscription_id
}}

module "{MODULE_ID.replace('-', '_')}" {{
  source = "git::https://github.com/{OWNER}/{MODULE_REPO}.git//{contract['path']}?ref=main"
{chr(10).join(module_args)}
}}
'''
(tfdir / "main.tf").write_text(main, encoding="utf-8")
(tfdir / "variables.tf").write_text("\n".join(variables), encoding="utf-8")
(tfdir / "terraform.tfvars.example.json").write_text(json.dumps(tfvars, indent=2) + "\n", encoding="utf-8")
(tfdir / ".gitignore").write_text(".terraform/\n*.tfstate\n*.tfstate.*\n*.tfplan\ncrash.log\n", encoding="utf-8")
(out / "README.md").write_text(
    f"# Infrastructure: {MODULE_ID}\n\n"
    f"Generated from the approved module contract in {MODULE_REPO}.\n\n"
    "Review terraform/variables.tf and terraform/terraform.tfvars.example.json. "
    "Never commit credentials or state files.\n\n"
    "This repository contains generated Terraform configuration; creating the repository does not deploy resources. "
    "Configure a remote AzureRM backend and GitHub Actions secrets/environment approvals before running terraform apply.\n",
    encoding="utf-8",
)
print(f"Generated root for {MODULE_ID} from {raw_url}")
