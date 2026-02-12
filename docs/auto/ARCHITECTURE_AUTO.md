# Architecture (Auto-Generated)

**Generated:** 2026-02-12 04:13:55 **Project:** /home/runner/work/repo-standards/repo-standards

## Overview

Analyzed **5** Python modules containing:

- **4** classes
- **78** functions
- **0** async functions

### Detected Patterns

- ❌ **Api**
- ❌ **Async**
- ✅ **Cli**
- ❌ **Database**
- ❌ **Dataclass**
- ❌ **Orm**
- ❌ **Server**
- ✅ **State Machine**
- ✅ **Workflows**

## Flowchart Diagram

```mermaid
flowchart TD
    Start([Start]) --> Init[Initialize]
    Init --> rungitcommand[run_git_command]
    Init --> main[main]
    main --> End([End])
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> GenerateStateDiagram
    GenerateStateDiagram --> [*]
```

## Sequence Diagram

*Sequence diagram not applicable for this codebase.*

## Architecture Diagram

```mermaid
architecture-beta
    group scripts(cloud)[Scripts]
        service scripts_changelog(server)[changelog] in scripts
        service scripts_generate_architecture(server)[generate_architecture] in scripts
        service scripts_generate_workflow_registry(server)[generate_workflow_registry] in scripts
    end
    group docs(cloud)[Docs]
        service docs_conf(server)[conf] in docs
    end
```

## Er Diagram

*Er diagram not applicable for this codebase.*

## Class Diagram

```mermaid
classDiagram
    class scripts_generate_architecture_CodeAnalyzer {
        +__init__(root_path)
        +analyze()
        +_should_ignore(path)
        +_analyze_file(filepath)
        +_get_name(node)
    }
    class scripts_generate_architecture_DiagramGenerator {
        +__init__(analyzer)
        +generate_flowchart()
        +generate_state_diagram()
        +generate_sequence_diagram()
        +generate_architecture_diagram()
    }
    class scripts_generate_workflow_registry_WorkflowParser {
        +KNOWN_TOOLS
        +BASH_CHECK_PATTERNS
        +__init__(root_path)
        +parse_all()
        +_parse_workflows()
        +_extract_workflow(filename, data)
        +_detect_tools_in_steps(steps, job_id)
    }
    class scripts_generate_workflow_registry_RegistryDocGenerator {
        +__init__(parser)
        +generate()
        +_header()
        +_precommit_vs_ci()
        +_workflow_registry()
    }
```

## Journey Diagram

*Journey diagram not applicable for this codebase.*

## Mindmap Diagram

```mermaid
mindmap
  root((Project))
    docs
      conf
    scripts
      changelog
      generate_architecture
      generate_workflow_registry
      repo_map
```

## Workflow Pipeline Diagram

```mermaid
flowchart TD

    Push -->|Doc Changes| Docs[Build Docs]
    Docs --> reusable_docker_build[Docker Build Standards]
    Docs --> reusable_update_architecture[Update Architecture Documentat]
```

## Workflow Triggers Diagram

```mermaid
graph TD
    reusable_makefile_ci[Makefile Standards Enforcement]
    reusable_config_validation[Config Standards Validation]
    reusable_yaml_ci[YAML Standards Enforcement]
    reusable_docker_build[Docker Build Standards]
    reusable_python_ci[Python Standards Enforcement]
    reusable_update_architecture[Update Architecture Documentation]
    reusable_shell_ci[Shell Script Standards Enforcement]
    reusable_pre_commit[Pre-commit Standards Enforcement]
    reusable_update_docs[Update Documentation (Reusable)]
    reusable_quality_checks[Advanced Quality Checks]
```

## Workflow Jobs Diagram

```mermaid
flowchart LR
    subgraph reusable_python_ci[Python Standards Enforcement]
        validate_python_version[validate-python-version]
        python_lint[python-lint]
        python_syntax[python-syntax]
        validate_python_version --> python_lint
        validate_python_version --> python_syntax
    end
```

## Development Workflows

### GitHub Workflows Summary

| Workflow                           | Triggers | Jobs                                                        |
| ---------------------------------- | -------- | ----------------------------------------------------------- |
| Config Standards Validation        |          | validate-configs                                            |
| Docker Build Standards             |          | docker-build                                                |
| Makefile Standards Enforcement     |          | validate-makefile                                           |
| Pre-commit Standards Enforcement   |          | pre-commit                                                  |
| Python Standards Enforcement       |          | validate-python-version, python-lint, python-syntax         |
| Advanced Quality Checks            |          | detect-unused-python, detect-unused-shell, markdown-lint... |
| Shell Script Standards Enforcement |          | shellcheck, bash-syntax                                     |
| Update Architecture Documentation  |          | generate-architecture                                       |
| Update Documentation (Reusable)    |          | update-and-build-docs                                       |
| YAML Standards Enforcement         |          | validate-yaml                                               |

## Module Summary

### `docs.conf`

- **Classes:** 0
- **Functions:** 0
- **Async Functions:** 0

### `scripts.changelog`

changelog.py - Generate changelog from git history

Automatically generates and maintains a CHANGELOG.md file following the Keep a Changelog format using conventional
commits.

Usage: python3 chan...

- **Classes:** 0
- **Functions:** 8
- **Async Functions:** 0

### `scripts.generate_architecture`

generate_architecture.py - Comprehensive Architecture Diagram Generator

Generates multiple Mermaid diagram types based on codebase analysis:

- flowchart: Control flow and process flows

- stateDiagram...

- **Classes:** 2

- **Functions:** 26

- **Async Functions:** 0

### `scripts.generate_workflow_registry`

generate_workflow_registry.py - Generate workflow registry and tool coverage matrix

Parses all reusable GitHub Actions workflow YAML files and the pre-commit config to produce a comprehensive referen...

- **Classes:** 2
- **Functions:** 32
- **Async Functions:** 0

### `scripts.repo_map`

repo_map.py - Generate repository structure documentation

Automatically generates comprehensive repository structure documentation including directory trees, file descriptions,
and categorized overvi...

- **Classes:** 0
- **Functions:** 12
- **Async Functions:** 0

______________________________________________________________________

*Generated by: `generate_architecture.py` from repo-standards*
