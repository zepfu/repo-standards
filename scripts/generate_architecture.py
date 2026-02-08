#!/usr/bin/env python3
"""
generate_architecture.py - Comprehensive Architecture Diagram Generator

Generates multiple Mermaid diagram types based on codebase analysis:
- flowchart: Control flow and process flows
- stateDiagram-v2: State machines and lifecycle
- sequenceDiagram: API calls and interactions
- architecture-beta: System architecture (new Mermaid syntax)
- erDiagram: Data models and relationships
- classDiagram: OOP structure
- gitGraph: Development workflow (if .git present)
- gantt: Project timeline (if milestones detected)
- journey: User flows (if UI patterns detected)
- mindmap: Concept relationships

Usage:
    python3 generate_architecture.py
    python3 generate_architecture.py --diagrams flowchart,sequence,class
    python3 generate_architecture.py --all-diagrams
"""

import argparse
import ast
import datetime
from collections import defaultdict
from pathlib import Path
from typing import List, Optional

import yaml


class CodeAnalyzer:
    """Analyzes Python codebase structure and relationships."""

    def __init__(self, root_path: Path = Path(".")):
        self.root_path = root_path
        self.modules = {}
        self.imports_graph = defaultdict(set)
        self.classes = {}
        self.functions = {}
        self.state_machines = []
        self.api_endpoints = []
        self.data_models = []
        self.workflows = {}  # GitHub workflows
        self.patterns = {
            "server": False,
            "api": False,
            "cli": False,
            "database": False,
            "async": False,
            "state_machine": False,
            "orm": False,
            "dataclass": False,
            "workflows": False,
        }

    def analyze(self):
        """Analyze entire codebase."""
        print(f"Analyzing {self.root_path}...")

        py_files = list(self.root_path.rglob("*.py"))
        py_files = [f for f in py_files if not self._should_ignore(f)]

        print(f"Found {len(py_files)} Python files")

        for py_file in py_files:
            self._analyze_file(py_file)

        # Analyze workflows
        self._analyze_workflows()

        self._detect_patterns()

        return self

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        ignore_patterns = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "build",
            "dist",
            ".pytest_cache",
            ".tox",
            "node_modules",
            "_build",
        }
        return any(pattern in path.parts for pattern in ignore_patterns)

    def _analyze_file(self, filepath: Path):
        """Analyze a single Python file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(filepath))

            rel_path = filepath.relative_to(self.root_path)
            module_name = str(rel_path).replace("/", ".").replace(".py", "")

            module_info = {
                "path": filepath,
                "imports": set(),
                "classes": [],
                "functions": [],
                "async_functions": [],
                "decorators": set(),
                "docstring": ast.get_docstring(tree),
                "has_state_logic": False,
                "api_routes": [],
            }

            # Walk AST
            for node in ast.walk(tree):
                # Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info["imports"].add(alias.name)
                        self.imports_graph[module_name].add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info["imports"].add(node.module)
                        self.imports_graph[module_name].add(node.module)

                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "bases": [self._get_name(b) for b in node.bases],
                        "methods": [],
                        "attributes": [],
                        "decorators": [self._get_name(d) for d in node.decorator_list],
                        "docstring": ast.get_docstring(node),
                    }

                    # Analyze class body
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(
                                {
                                    "name": item.name,
                                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                                    "args": [a.arg for a in item.args.args if a.arg != "self"],
                                }
                            )
                        elif isinstance(item, ast.AnnAssign):
                            # Type annotations (dataclass fields, etc)
                            if isinstance(item.target, ast.Name):
                                class_info["attributes"].append(item.target.id)

                    module_info["classes"].append(class_info)
                    self.classes[f"{module_name}.{node.name}"] = class_info

                    # Check for state machine patterns
                    method_names = [m["name"] for m in class_info["methods"]]
                    if any(
                        s in " ".join(method_names).lower()
                        for s in ["state", "transition", "handle"]
                    ):
                        module_info["has_state_logic"] = True
                        self.state_machines.append(
                            {
                                "module": module_name,
                                "class": node.name,
                                "methods": method_names,
                            }
                        )

                    # Check for data models (ORM, dataclass)
                    if any(base in ["Model", "Base", "Document"] for base in class_info["bases"]):
                        self.data_models.append(
                            {
                                "module": module_name,
                                "class": node.name,
                                "attributes": class_info["attributes"],
                            }
                        )

                # Functions
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "decorators": [self._get_name(d) for d in node.decorator_list],
                        "args": [a.arg for a in node.args.args],
                    }

                    if func_info["is_async"]:
                        module_info["async_functions"].append(func_info)
                    else:
                        module_info["functions"].append(func_info)

                    # Collect decorators
                    for dec in node.decorator_list:
                        dec_name = self._get_name(dec)
                        module_info["decorators"].add(dec_name)

                        # Check for API routes
                        if any(
                            route in dec_name.lower()
                            for route in ["route", "get", "post", "put", "delete", "patch"]
                        ):
                            # Try to extract path
                            path = self._extract_route_path(dec)
                            self.api_endpoints.append(
                                {
                                    "module": module_name,
                                    "function": node.name,
                                    "method": self._extract_http_method(dec_name),
                                    "path": path,
                                }
                            )
                            module_info["api_routes"].append(
                                {
                                    "function": node.name,
                                    "path": path,
                                }
                            )

            self.modules[module_name] = module_info

        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}")

    def _get_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return str(node)

    def _extract_route_path(self, decorator) -> str:
        """Extract path from route decorator."""
        if isinstance(decorator, ast.Call) and decorator.args:
            arg = decorator.args[0]
            if isinstance(arg, ast.Constant):
                return arg.value
        return "/unknown"

    def _extract_http_method(self, decorator_name: str) -> str:
        """Extract HTTP method from decorator name."""
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            if method.lower() in decorator_name.lower():
                return method
        return "GET"

    def _analyze_workflows(self):
        """Analyze GitHub workflow files."""
        workflows_dir = self.root_path / ".github" / "workflows"

        if not workflows_dir.exists():
            return

        for yaml_file in workflows_dir.glob("*.yml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    workflow = yaml.safe_load(f)

                if not workflow:
                    continue

                workflow_name = yaml_file.stem

                workflow_info = {
                    "name": workflow.get("name", workflow_name),
                    "file": yaml_file.name,
                    "triggers": self._extract_triggers(workflow.get("on", {})),
                    "jobs": {},
                    "job_dependencies": {},
                }

                # Extract jobs
                jobs = workflow.get("jobs", {})
                for job_id, job_config in jobs.items():
                    workflow_info["jobs"][job_id] = {
                        "name": job_config.get("name", job_id),
                        "runs_on": job_config.get("runs-on", "unknown"),
                        "needs": job_config.get("needs", []),
                        "steps": len(job_config.get("steps", [])),
                    }

                    # Track dependencies
                    needs = job_config.get("needs", [])
                    if needs:
                        if isinstance(needs, str):
                            needs = [needs]
                        workflow_info["job_dependencies"][job_id] = needs

                self.workflows[workflow_name] = workflow_info

            except Exception as e:
                print(f"Warning: Could not analyze workflow {yaml_file}: {e}")

    def _extract_triggers(self, on_config) -> List[str]:
        """Extract trigger types from workflow 'on' config."""
        if isinstance(on_config, str):
            return [on_config]
        elif isinstance(on_config, list):
            return on_config
        elif isinstance(on_config, dict):
            return list(on_config.keys())
        return []

    def _detect_patterns(self):
        """Detect common architectural patterns."""
        all_imports = set()
        all_decorators = set()

        for module_info in self.modules.values():
            all_imports.update(module_info["imports"])
            all_decorators.update(module_info["decorators"])

            if module_info["async_functions"]:
                self.patterns["async"] = True

            if module_info["has_state_logic"]:
                self.patterns["state_machine"] = True

        # Server frameworks
        server_imports = {"fastapi", "flask", "django", "aiohttp", "tornado", "asyncio"}
        self.patterns["server"] = bool(all_imports & server_imports)

        # API patterns
        api_decorators = {"route", "get", "post", "put", "delete", "api", "endpoint"}
        self.patterns["api"] = any(dec in str(all_decorators).lower() for dec in api_decorators)

        # CLI
        cli_imports = {"argparse", "click", "typer"}
        self.patterns["cli"] = bool(all_imports & cli_imports)

        # Database
        db_imports = {"sqlalchemy", "psycopg2", "pymongo", "redis", "sqlite3", "peewee"}
        self.patterns["database"] = bool(all_imports & db_imports)

        # ORM
        orm_imports = {"sqlalchemy", "django.db", "peewee", "tortoise"}
        self.patterns["orm"] = bool(all_imports & orm_imports)

        # Dataclass
        dataclass_decorators = {"dataclass", "dataclasses.dataclass"}
        self.patterns["dataclass"] = any(dec in str(all_decorators) for dec in dataclass_decorators)

        # Workflows
        self.patterns["workflows"] = len(self.workflows) > 0


class DiagramGenerator:
    """Generates various Mermaid diagram types from analyzed code."""

    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer

    def generate_flowchart(self) -> Optional[str]:
        """Generate flowchart for main execution flow."""
        modules = self.analyzer.modules

        # Find entry point (main, app, cli)
        entry_module = self._find_entry_point()
        if not entry_module:
            return None

        diagram = "```mermaid\nflowchart TD\n"
        diagram += "    Start([Start]) --> Init[Initialize]\n"

        # Get main functions
        entry_info = modules.get(entry_module)
        if entry_info:
            main_funcs = [
                f
                for f in entry_info["functions"]
                if any(kw in f["name"].lower() for kw in ["main", "run", "start", "execute"])
            ]

            if main_funcs:
                for func in main_funcs[:3]:
                    safe_name = func["name"].replace("_", "")
                    diagram += f"    Init --> {safe_name}[{func['name']}]\n"

                    # Check if it calls other modules
                    for imp_module in entry_info["imports"]:
                        if imp_module in modules:
                            diagram += f"    {safe_name} --> {imp_module.replace('.', '_')}[{imp_module}]\n"

        diagram += f"    {safe_name if main_funcs else 'Init'} --> End([End])\n"
        diagram += "```\n"
        return diagram

    def generate_state_diagram(self) -> Optional[str]:
        """Generate state machine diagram."""
        if not self.analyzer.patterns["state_machine"]:
            return None

        diagram = "```mermaid\nstateDiagram-v2\n"
        diagram += "    [*] --> Idle\n"

        # Use detected state machines
        for sm in self.analyzer.state_machines[:2]:  # Limit to 2
            methods = sm["methods"]

            # Look for state-related methods
            states = set()
            for method in methods:
                # Extract potential states from method names
                if "state" in method.lower() or "handle" in method.lower():
                    # Convert handle_active → Active
                    state = method.replace("handle_", "").replace("_", " ").title().replace(" ", "")
                    if state and state not in ["Handle", "State"]:
                        states.add(state)

            # Add transitions
            prev_state = "Idle"
            for state in sorted(states)[:5]:  # Limit states
                diagram += f"    {prev_state} --> {state}\n"
                prev_state = state

            if prev_state != "Idle":
                diagram += f"    {prev_state} --> [*]\n"

        diagram += "```\n"
        return diagram

    def generate_sequence_diagram(self) -> Optional[str]:
        """Generate sequence diagram for API interactions."""
        if not self.analyzer.patterns["api"] or not self.analyzer.api_endpoints:
            return None

        diagram = "```mermaid\nsequenceDiagram\n"
        diagram += "    participant Client\n"
        diagram += "    participant API\n"

        # Find service/handler modules
        services = [
            m
            for m in self.analyzer.modules.keys()
            if any(kw in m.lower() for kw in ["service", "handler", "controller"])
        ]

        if services:
            diagram += "    participant Service\n"

        if self.analyzer.patterns["database"]:
            diagram += "    participant DB\n"

        # Add typical flow for first few endpoints
        for endpoint in self.analyzer.api_endpoints[:3]:
            method = endpoint["method"]
            path = endpoint["path"]

            diagram += f"\n    Note over Client,API: {method} {path}\n"
            diagram += f"    Client->>+API: {method} {path}\n"

            if services:
                diagram += "    API->>+Service: process_request()\n"

                if self.analyzer.patterns["database"]:
                    diagram += "    Service->>+DB: query()\n"
                    diagram += "    DB-->>-Service: result\n"

                diagram += "    Service-->>-API: response\n"

            diagram += "    API-->>-Client: 200 OK\n"

        diagram += "```\n"
        return diagram

    def generate_architecture_diagram(self) -> Optional[str]:
        """Generate architecture-beta diagram (new Mermaid syntax)."""
        diagram = "```mermaid\narchitecture-beta\n"

        # Group modules by directory
        groups = defaultdict(list)
        for module in self.analyzer.modules.keys():
            group = module.split(".")[0] if "." in module else "root"
            groups[group].append(module)

        # Add groups and services
        for group, modules in groups.items():
            if group == "root":
                continue

            diagram += f"    group {group}(cloud)[{group.title()}]\n"

            for module in modules[:3]:  # Limit per group
                safe_name = module.replace(".", "_").replace("-", "_")
                display_name = module.split(".")[-1]
                diagram += f"        service {safe_name}(server)[{display_name}] in {group}\n"

            diagram += "    end\n"

        # Add connections
        for module, imports in list(self.analyzer.imports_graph.items())[:5]:
            module_safe = module.replace(".", "_").replace("-", "_")
            for imp in imports:
                if imp in self.analyzer.modules:
                    imp_safe = imp.replace(".", "_").replace("-", "_")
                    diagram += f"    {module_safe}:L -- R:{imp_safe}\n"

        diagram += "```\n"
        return diagram

    def generate_er_diagram(self) -> Optional[str]:
        """Generate ER diagram for data models."""
        if not self.analyzer.data_models and not self.analyzer.patterns["dataclass"]:
            return None

        diagram = "```mermaid\nerDiagram\n"

        # Use detected data models
        models = self.analyzer.data_models[:10]  # Limit

        if not models:
            # Fall back to classes with attributes
            for class_name, class_info in list(self.analyzer.classes.items())[:10]:
                if class_info["attributes"]:
                    models.append(
                        {
                            "class": class_name.split(".")[-1],
                            "attributes": class_info["attributes"],
                        }
                    )

        for model in models:
            entity_name = model.get("class", "Unknown")
            attributes = model.get("attributes", [])

            if attributes:
                diagram += f"    {entity_name} {{\n"
                for attr in attributes[:10]:  # Limit attributes
                    diagram += f"        string {attr}\n"
                diagram += "    }\n"

        # Add relationships (simplified - look for foreign key patterns)
        added_relations = set()
        for i, model1 in enumerate(models):
            entity1 = model1.get("class", "Unknown")
            attrs1 = model1.get("attributes", [])

            for model2 in models[i + 1 :]:
                entity2 = model2.get("class", "Unknown")

                # Check if entity1 references entity2
                if any(entity2.lower() in attr.lower() for attr in attrs1):
                    rel = (entity1, entity2)
                    if rel not in added_relations:
                        diagram += f"    {entity1} ||--o{{ {entity2} : has\n"
                        added_relations.add(rel)

        diagram += "```\n"
        return diagram

    def generate_class_diagram(self) -> Optional[str]:
        """Generate class diagram for OOP structure."""
        if not self.analyzer.classes:
            return None

        diagram = "```mermaid\nclassDiagram\n"

        for class_name, class_info in list(self.analyzer.classes.items())[:15]:
            safe_name = class_name.replace(".", "_").replace("-", "_")

            diagram += f"    class {safe_name} {{\n"

            # Add attributes
            for attr in class_info["attributes"][:5]:
                diagram += f"        +{attr}\n"

            # Add methods
            for method in class_info["methods"][:5]:
                args = ", ".join(method["args"][:3])
                diagram += f"        +{method['name']}({args})\n"

            diagram += "    }\n"

            # Add inheritance
            for base in class_info["bases"]:
                if base and base != "object":
                    base_safe = base.replace(".", "_").replace("-", "_")
                    # Check if base is in our classes
                    if any(base in cn for cn in self.analyzer.classes.keys()):
                        diagram += f"    {base_safe} <|-- {safe_name}\n"

        diagram += "```\n"
        return diagram

    def generate_journey_diagram(self) -> Optional[str]:
        """Generate user journey if UI/API flow detected."""
        if not self.analyzer.patterns["api"]:
            return None

        diagram = "```mermaid\njourney\n"
        diagram += "    title API User Journey\n"

        # Group endpoints by path prefix
        endpoints_by_prefix = defaultdict(list)
        for ep in self.analyzer.api_endpoints:
            prefix = ep["path"].split("/")[1] if "/" in ep["path"] else "root"
            endpoints_by_prefix[prefix].append(ep)

        # Create journey sections
        for prefix, endpoints in list(endpoints_by_prefix.items())[:3]:
            diagram += f"    section {prefix.title()}\n"
            for ep in endpoints[:3]:
                score = 5 if ep["method"] == "GET" else 3
                diagram += f"      {ep['method']} {ep['path']}: {score}: User\n"

        diagram += "```\n"
        return diagram

    def generate_mindmap(self) -> Optional[str]:
        """Generate mindmap of module organization."""
        diagram = "```mermaid\nmindmap\n"
        diagram += "  root((Project))\n"

        # Group by top-level directory
        groups = defaultdict(list)
        for module in self.analyzer.modules.keys():
            parts = module.split(".")
            group = parts[0]
            groups[group].append(module)

        for group, modules in sorted(groups.items())[:8]:
            diagram += f"    {group}\n"
            for module in modules[:5]:
                display = module.split(".")[-1]
                diagram += f"      {display}\n"

        diagram += "```\n"
        return diagram

    def _find_entry_point(self) -> Optional[str]:
        """Find likely entry point module."""
        candidates = ["__main__", "main", "app", "server", "api", "cli", "gateway"]

        for module_name in self.analyzer.modules.keys():
            for candidate in candidates:
                if candidate in module_name.lower():
                    return module_name

        return list(self.analyzer.modules.keys())[0] if self.analyzer.modules else None

    def generate_workflow_pipeline(self) -> Optional[str]:
        """Generate CI/CD pipeline diagram from workflows."""
        if not self.analyzer.workflows:
            return None

        diagram = "```mermaid\nflowchart TD\n"

        # Identify workflow types
        ci_workflows = []
        publish_workflows = []
        doc_workflows = []
        release_workflows = []
        other_workflows = []

        for name, info in self.analyzer.workflows.items():
            triggers = info["triggers"]
            workflow_name = info["name"]

            if any(t in ["push", "pull_request"] for t in triggers):
                ci_workflows.append((name, info))
            elif "workflow_run" in triggers or "workflow_call" in triggers:
                publish_workflows.append((name, info))
            elif any("doc" in t.lower() for t in triggers + [workflow_name.lower()]):
                doc_workflows.append((name, info))
            elif "release" in triggers or any("release" in workflow_name.lower() for _ in [1]):
                release_workflows.append((name, info))
            else:
                other_workflows.append((name, info))

        # Build diagram
        if ci_workflows:
            diagram += "    Push[Code Push] --> CI{CI Checks}\n"
            for name, info in ci_workflows[:2]:
                safe_name = name.replace("-", "_").replace(".", "_")
                display = info["name"][:30]
                diagram += f"    CI --> {safe_name}[{display}]\n"

        if publish_workflows:
            diagram += "\n    CI -->|Success| Publish[Publish]\n"
            for name, info in publish_workflows[:2]:
                safe_name = name.replace("-", "_").replace(".", "_")
                display = info["name"][:30]
                diagram += f"    Publish --> {safe_name}[{display}]\n"

        if doc_workflows:
            diagram += "\n    Push -->|Doc Changes| Docs[Build Docs]\n"
            for name, info in doc_workflows[:2]:
                safe_name = name.replace("-", "_").replace(".", "_")
                display = info["name"][:30]
                diagram += f"    Docs --> {safe_name}[{display}]\n"

        if release_workflows:
            diagram += "\n    Tag[Release Tag] --> Release[Release Process]\n"
            for name, info in release_workflows[:2]:
                safe_name = name.replace("-", "_").replace(".", "_")
                display = info["name"][:30]
                diagram += f"    Release --> {safe_name}[{display}]\n"

        diagram += "```\n"
        return diagram

    def generate_workflow_triggers(self) -> Optional[str]:
        """Generate workflow trigger relationship diagram."""
        if not self.analyzer.workflows:
            return None

        diagram = "```mermaid\ngraph TD\n"

        # Add trigger nodes
        triggers_seen = set()

        for workflow_name, info in self.analyzer.workflows.items():
            safe_name = workflow_name.replace("-", "_").replace(".", "_")
            display_name = info["name"][:40]

            diagram += f"    {safe_name}[{display_name}]\n"

            for trigger in info["triggers"]:
                trigger_safe = trigger.replace("-", "_").replace(".", "_")

                if trigger_safe not in triggers_seen:
                    if trigger in ["push", "pull_request"]:
                        diagram += f"    {trigger_safe}{{Git {trigger.title()}}}\n"
                    elif trigger == "schedule":
                        diagram += f"    {trigger_safe}[Schedule/Cron]\n"
                    elif trigger == "workflow_dispatch":
                        diagram += f"    {trigger_safe}[Manual Trigger]\n"
                    elif trigger in ["workflow_run", "workflow_call"]:
                        diagram += f"    {trigger_safe}[Workflow Dependency]\n"
                    else:
                        diagram += f"    {trigger_safe}[{trigger.title()}]\n"

                    triggers_seen.add(trigger_safe)

                diagram += f"    {trigger_safe} --> {safe_name}\n"

        diagram += "```\n"
        return diagram

    def generate_workflow_jobs(self) -> Optional[str]:
        """Generate job dependency diagram for workflows."""
        if not self.analyzer.workflows:
            return None

        diagram = "```mermaid\nflowchart LR\n"

        # Find workflow with most complex job dependencies
        max_jobs = 0
        selected_workflow = None

        for name, info in self.analyzer.workflows.items():
            if len(info["job_dependencies"]) > max_jobs:
                max_jobs = len(info["job_dependencies"])
                selected_workflow = (name, info)

        if not selected_workflow:
            # No dependencies, just show jobs in sequence
            for name, info in list(self.analyzer.workflows.items())[:1]:
                jobs = list(info["jobs"].keys())
                if jobs:
                    for i, job in enumerate(jobs[:5]):
                        safe_job = job.replace("-", "_").replace(".", "_")
                        diagram += f"    Job{i}[{job}]\n"
                        if i > 0:
                            diagram += f"    Job{i-1} --> Job{i}\n"
        else:
            # Show job dependencies
            name, info = selected_workflow
            diagram += f"    subgraph {name.replace('-', '_')}[{info['name']}]\n"

            # Add all jobs
            for job_id in info["jobs"].keys():
                safe_job = job_id.replace("-", "_").replace(".", "_")
                diagram += f"        {safe_job}[{job_id}]\n"

            # Add dependencies
            for job_id, deps in info["job_dependencies"].items():
                safe_job = job_id.replace("-", "_").replace(".", "_")
                for dep in deps:
                    safe_dep = dep.replace("-", "_").replace(".", "_")
                    diagram += f"        {safe_dep} --> {safe_job}\n"

            diagram += "    end\n"

        diagram += "```\n"
        return diagram

    def generate_workflow_summary(self) -> Optional[str]:
        """Generate workflow summary table."""
        if not self.analyzer.workflows:
            return None

        summary = "### GitHub Workflows Summary\n\n"
        summary += "| Workflow | Triggers | Jobs |\n"
        summary += "|----------|----------|------|\n"

        for name, info in sorted(self.analyzer.workflows.items()):
            workflow_name = info["name"]
            triggers = ", ".join(info["triggers"][:3])
            if len(info["triggers"]) > 3:
                triggers += "..."
            jobs = ", ".join(list(info["jobs"].keys())[:3])
            if len(info["jobs"]) > 3:
                jobs += "..."

            summary += f"| {workflow_name} | {triggers} | {jobs} |\n"

        summary += "\n"
        return summary


def generate_documentation(analyzer: CodeAnalyzer, args) -> str:
    """Generate complete architecture documentation."""
    generator = DiagramGenerator(analyzer)

    doc = f"""# Architecture (Auto-Generated)

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project:** {analyzer.root_path.absolute()}

## Overview

Analyzed **{len(analyzer.modules)}** Python modules containing:
- **{len(analyzer.classes)}** classes
- **{sum(len(m['functions']) for m in analyzer.modules.values())}** functions
- **{sum(len(m['async_functions']) for m in analyzer.modules.values())}** async functions

### Detected Patterns

"""

    for pattern, detected in sorted(analyzer.patterns.items()):
        icon = "✅" if detected else "❌"
        doc += f"- {icon} **{pattern.replace('_', ' ').title()}**\n"

    # Determine which diagrams to generate
    diagram_methods = {
        "flowchart": generator.generate_flowchart,
        "state": generator.generate_state_diagram,
        "sequence": generator.generate_sequence_diagram,
        "architecture": generator.generate_architecture_diagram,
        "er": generator.generate_er_diagram,
        "class": generator.generate_class_diagram,
        "journey": generator.generate_journey_diagram,
        "mindmap": generator.generate_mindmap,
        "workflow_pipeline": generator.generate_workflow_pipeline,
        "workflow_triggers": generator.generate_workflow_triggers,
        "workflow_jobs": generator.generate_workflow_jobs,
    }

    # Filter diagrams if specified
    if hasattr(args, "diagrams") and args.diagrams:
        requested = set(args.diagrams.split(","))
        diagram_methods = {k: v for k, v in diagram_methods.items() if k in requested}

    # Generate each diagram type
    for name, method in diagram_methods.items():
        doc += f"\n## {name.replace('_', ' ').title()} Diagram\n\n"
        diagram = method()
        if diagram:
            doc += diagram + "\n"
        else:
            doc += f"*{name.title()} diagram not applicable for this codebase.*\n\n"

    # Workflow summary table
    if analyzer.workflows:
        doc += "\n## Development Workflows\n\n"
        workflow_summary = generator.generate_workflow_summary()
        if workflow_summary:
            doc += workflow_summary

    # Module summary
    doc += "## Module Summary\n\n"
    for module_name, module_info in sorted(analyzer.modules.items()):
        doc += f"### `{module_name}`\n\n"
        if module_info["docstring"]:
            summary = module_info["docstring"][:200]
            doc += f"{summary}{'...' if len(module_info['docstring']) > 200 else ''}\n\n"

        doc += f"- **Classes:** {len(module_info['classes'])}\n"
        doc += f"- **Functions:** {len(module_info['functions'])}\n"
        doc += f"- **Async Functions:** {len(module_info['async_functions'])}\n"

        if module_info["api_routes"]:
            doc += f"- **API Routes:** {len(module_info['api_routes'])}\n"

        doc += "\n"

    doc += "---\n\n*Generated by: `generate_architecture.py` from repo-standards*\n"

    return doc


def main():
    parser = argparse.ArgumentParser(
        description="Generate architecture documentation with multiple diagram types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Diagram Types:
  flowchart          - Execution flow and process flows
  state              - State machines and lifecycle (stateDiagram-v2)
  sequence           - API calls and interactions (sequenceDiagram)
  architecture       - System architecture (architecture-beta)
  er                 - Data models and relationships (erDiagram)
  class              - OOP structure (classDiagram)
  journey            - User flows (journey)
  mindmap            - Concept relationships (mindmap)
  workflow_pipeline  - CI/CD pipeline (flowchart)
  workflow_triggers  - Workflow trigger relationships (graph)
  workflow_jobs      - Job dependencies (flowchart)

Examples:
  python3 generate_architecture.py
  python3 generate_architecture.py --diagrams flowchart,sequence,class
  python3 generate_architecture.py --diagrams workflow_pipeline,workflow_triggers
  python3 generate_architecture.py --all-diagrams --output docs/ARCH.md
        """,
    )
    parser.add_argument("--root", "-r", default=".", help="Project root directory")
    parser.add_argument(
        "--output", "-o", default="docs/ARCHITECTURE_AUTO.md", help="Output file path"
    )
    parser.add_argument(
        "--diagrams", "-d", help="Comma-separated list of diagram types to generate"
    )
    parser.add_argument(
        "--all-diagrams", action="store_true", help="Generate all applicable diagram types"
    )

    args = parser.parse_args()

    # Analyze codebase
    analyzer = CodeAnalyzer(Path(args.root))
    analyzer.analyze()

    # Generate documentation
    content = generate_documentation(analyzer, args)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(content)

    print(f"\n✓ Generated architecture documentation: {output_path}")
    print(f"  Analyzed: {len(analyzer.modules)} modules")
    print(f"  Found: {len(analyzer.classes)} classes")
    print(f"  API endpoints: {len(analyzer.api_endpoints)}")
    print(f"  Data models: {len(analyzer.data_models)}")
    print(f"  State machines: {len(analyzer.state_machines)}")
    print(f"  Workflows: {len(analyzer.workflows)}")

    detected = [k for k, v in analyzer.patterns.items() if v]
    if detected:
        print(f"  Patterns: {', '.join(detected)}")


if __name__ == "__main__":
    main()
