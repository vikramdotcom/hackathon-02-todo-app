"""
Infrastructure as Code (IaC) Generator

Generate infrastructure configuration files for various platforms.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import yaml

logger = logging.getLogger(__name__)


class TerraformGenerator:
    """Generate Terraform configuration."""

    def __init__(self):
        """Initialize Terraform generator."""
        self.resources: List[Dict[str, Any]] = []
        self.variables: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}

    def add_resource(
        self,
        resource_type: str,
        name: str,
        config: Dict[str, Any]
    ):
        """Add Terraform resource."""
        self.resources.append({
            "type": resource_type,
            "name": name,
            "config": config
        })

    def add_variable(self, name: str, var_type: str, default: Any = None):
        """Add Terraform variable."""
        self.variables[name] = {
            "type": var_type,
            "default": default
        }

    def add_output(self, name: str, value: str):
        """Add Terraform output."""
        self.outputs[name] = {"value": value}

    def generate(self) -> str:
        """Generate Terraform configuration."""
        config = []

        # Variables
        if self.variables:
            config.append("# Variables")
            for name, var in self.variables.items():
                config.append(f'variable "{name}" {{')
                config.append(f'  type    = {var["type"]}')
                if var["default"] is not None:
                    config.append(f'  default = "{var["default"]}"')
                config.append("}")
                config.append("")

        # Resources
        if self.resources:
            config.append("# Resources")
            for resource in self.resources:
                config.append(f'resource "{resource["type"]}" "{resource["name"]}" {{')
                for key, value in resource["config"].items():
                    if isinstance(value, str):
                        config.append(f'  {key} = "{value}"')
                    else:
                        config.append(f'  {key} = {value}')
                config.append("}")
                config.append("")

        # Outputs
        if self.outputs:
            config.append("# Outputs")
            for name, output in self.outputs.items():
                config.append(f'output "{name}" {{')
                config.append(f'  value = {output["value"]}')
                config.append("}")
                config.append("")

        return "\n".join(config)


class KubernetesManifestGenerator:
    """Generate Kubernetes manifests."""

    def __init__(self):
        """Initialize Kubernetes manifest generator."""
        self.manifests: List[Dict[str, Any]] = []

    def add_deployment(
        self,
        name: str,
        namespace: str,
        image: str,
        replicas: int = 1,
        port: int = 8080
    ):
        """Add deployment manifest."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "ports": [
                                    {
                                        "containerPort": port
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        self.manifests.append(manifest)

    def add_service(
        self,
        name: str,
        namespace: str,
        port: int = 80,
        target_port: int = 8080,
        service_type: str = "ClusterIP"
    ):
        """Add service manifest."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "type": service_type,
                "selector": {
                    "app": name
                },
                "ports": [
                    {
                        "port": port,
                        "targetPort": target_port
                    }
                ]
            }
        }

        self.manifests.append(manifest)

    def add_ingress(
        self,
        name: str,
        namespace: str,
        host: str,
        service_name: str,
        service_port: int = 80
    ):
        """Add ingress manifest."""
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": service_name,
                                            "port": {
                                                "number": service_port
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        self.manifests.append(manifest)

    def generate_yaml(self) -> str:
        """Generate YAML manifests."""
        yaml_docs = []

        for manifest in self.manifests:
            yaml_docs.append(yaml.dump(manifest, default_flow_style=False))

        return "---\n".join(yaml_docs)


class DockerfileGenerator:
    """Generate Dockerfile."""

    def __init__(self, base_image: str = "python:3.11-slim"):
        """Initialize Dockerfile generator."""
        self.base_image = base_image
        self.instructions: List[str] = []

    def add_instruction(self, instruction: str):
        """Add Dockerfile instruction."""
        self.instructions.append(instruction)

    def set_workdir(self, workdir: str):
        """Set working directory."""
        self.add_instruction(f"WORKDIR {workdir}")

    def copy_files(self, source: str, dest: str):
        """Copy files."""
        self.add_instruction(f"COPY {source} {dest}")

    def run_command(self, command: str):
        """Run command."""
        self.add_instruction(f"RUN {command}")

    def expose_port(self, port: int):
        """Expose port."""
        self.add_instruction(f"EXPOSE {port}")

    def set_cmd(self, cmd: List[str]):
        """Set CMD."""
        cmd_str = json.dumps(cmd)
        self.add_instruction(f"CMD {cmd_str}")

    def generate(self) -> str:
        """Generate Dockerfile."""
        dockerfile = [f"FROM {self.base_image}"]
        dockerfile.extend(self.instructions)
        return "\n".join(dockerfile)


class DockerComposeGenerator:
    """Generate docker-compose.yml."""

    def __init__(self, version: str = "3.8"):
        """Initialize docker-compose generator."""
        self.version = version
        self.services: Dict[str, Dict[str, Any]] = {}
        self.networks: Dict[str, Dict[str, Any]] = {}
        self.volumes: Dict[str, Dict[str, Any]] = {}

    def add_service(
        self,
        name: str,
        image: str,
        ports: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        depends_on: Optional[List[str]] = None
    ):
        """Add service."""
        service = {"image": image}

        if ports:
            service["ports"] = ports

        if environment:
            service["environment"] = environment

        if depends_on:
            service["depends_on"] = depends_on

        self.services[name] = service

    def add_network(self, name: str, driver: str = "bridge"):
        """Add network."""
        self.networks[name] = {"driver": driver}

    def add_volume(self, name: str):
        """Add volume."""
        self.volumes[name] = {}

    def generate_yaml(self) -> str:
        """Generate docker-compose.yml."""
        compose = {"version": self.version}

        if self.services:
            compose["services"] = self.services

        if self.networks:
            compose["networks"] = self.networks

        if self.volumes:
            compose["volumes"] = self.volumes

        return yaml.dump(compose, default_flow_style=False)


class HelmChartGenerator:
    """Generate Helm chart."""

    def __init__(self, name: str, version: str = "0.1.0"):
        """Initialize Helm chart generator."""
        self.name = name
        self.version = version
        self.values: Dict[str, Any] = {}
        self.templates: Dict[str, str] = {}

    def set_values(self, values: Dict[str, Any]):
        """Set chart values."""
        self.values = values

    def add_template(self, name: str, content: str):
        """Add template."""
        self.templates[name] = content

    def generate_chart_yaml(self) -> str:
        """Generate Chart.yaml."""
        chart = {
            "apiVersion": "v2",
            "name": self.name,
            "version": self.version,
            "description": f"Helm chart for {self.name}"
        }

        return yaml.dump(chart, default_flow_style=False)

    def generate_values_yaml(self) -> str:
        """Generate values.yaml."""
        return yaml.dump(self.values, default_flow_style=False)


class CloudFormationGenerator:
    """Generate AWS CloudFormation template."""

    def __init__(self):
        """Initialize CloudFormation generator."""
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.parameters: Dict[str, Dict[str, Any]] = {}
        self.outputs: Dict[str, Dict[str, Any]] = {}

    def add_resource(
        self,
        logical_id: str,
        resource_type: str,
        properties: Dict[str, Any]
    ):
        """Add resource."""
        self.resources[logical_id] = {
            "Type": resource_type,
            "Properties": properties
        }

    def add_parameter(
        self,
        name: str,
        param_type: str,
        default: Optional[Any] = None
    ):
        """Add parameter."""
        param = {"Type": param_type}

        if default is not None:
            param["Default"] = default

        self.parameters[name] = param

    def add_output(self, name: str, value: Any, description: Optional[str] = None):
        """Add output."""
        output = {"Value": value}

        if description:
            output["Description"] = description

        self.outputs[name] = output

    def generate_json(self) -> str:
        """Generate CloudFormation JSON."""
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "CloudFormation template"
        }

        if self.parameters:
            template["Parameters"] = self.parameters

        if self.resources:
            template["Resources"] = self.resources

        if self.outputs:
            template["Outputs"] = self.outputs

        return json.dumps(template, indent=2)


class InfrastructureBuilder:
    """Build complete infrastructure configuration."""

    def __init__(self, project_name: str):
        """Initialize infrastructure builder."""
        self.project_name = project_name
        self.terraform = TerraformGenerator()
        self.kubernetes = KubernetesManifestGenerator()
        self.dockerfile = DockerfileGenerator()
        self.docker_compose = DockerComposeGenerator()

    def build_basic_infrastructure(
        self,
        image: str,
        replicas: int = 3,
        port: int = 8080
    ) -> Dict[str, str]:
        """Build basic infrastructure configuration."""
        # Dockerfile
        self.dockerfile.set_workdir("/app")
        self.dockerfile.copy_files("requirements.txt", ".")
        self.dockerfile.run_command("pip install -r requirements.txt")
        self.dockerfile.copy_files(".", ".")
        self.dockerfile.expose_port(port)
        self.dockerfile.set_cmd(["python", "main.py"])

        # Kubernetes
        self.kubernetes.add_deployment(
            self.project_name,
            "default",
            image,
            replicas,
            port
        )
        self.kubernetes.add_service(
            self.project_name,
            "default",
            80,
            port
        )

        # Docker Compose
        self.docker_compose.add_service(
            self.project_name,
            image,
            [f"{port}:{port}"]
        )

        return {
            "dockerfile": self.dockerfile.generate(),
            "kubernetes": self.kubernetes.generate_yaml(),
            "docker_compose": self.docker_compose.generate_yaml()
        }


# Global instances
terraform_generator = TerraformGenerator()
kubernetes_generator = KubernetesManifestGenerator()
dockerfile_generator = DockerfileGenerator()
docker_compose_generator = DockerComposeGenerator()
helm_chart_generator = HelmChartGenerator("todo-app")
cloudformation_generator = CloudFormationGenerator()


# Helper functions
def generate_dockerfile(
    base_image: str = "python:3.11-slim",
    workdir: str = "/app",
    port: int = 8080
) -> str:
    """Generate Dockerfile."""
    generator = DockerfileGenerator(base_image)
    generator.set_workdir(workdir)
    generator.copy_files("requirements.txt", ".")
    generator.run_command("pip install -r requirements.txt")
    generator.copy_files(".", ".")
    generator.expose_port(port)
    generator.set_cmd(["python", "main.py"])
    return generator.generate()


def generate_kubernetes_manifests(
    app_name: str,
    image: str,
    replicas: int = 3,
    port: int = 8080
) -> str:
    """Generate Kubernetes manifests."""
    generator = KubernetesManifestGenerator()
    generator.add_deployment(app_name, "default", image, replicas, port)
    generator.add_service(app_name, "default", 80, port)
    return generator.generate_yaml()


def generate_docker_compose(
    services: Dict[str, Dict[str, Any]]
) -> str:
    """Generate docker-compose.yml."""
    generator = DockerComposeGenerator()

    for name, config in services.items():
        generator.add_service(
            name,
            config["image"],
            config.get("ports"),
            config.get("environment"),
            config.get("depends_on")
        )

    return generator.generate_yaml()
