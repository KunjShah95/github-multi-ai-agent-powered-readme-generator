import os
import tempfile
from git import Repo
from core.a2a_protocol import A2AMessage


class AnalyzerAgent:

    # --- AGENT ROLE PROMPT ---
    # You are the AnalyzerAgent. Your role is to:
    # 1. Clone the target GitHub repository and analyze its structure, files, and technology stack.
    # 2. Detect programming languages, frameworks, and key files (e.g., main app, config, tests).
    # 3. Summarize the repository's purpose, architecture, and unique features.
    # 4. Output a structured summary for downstream agents (WriterAgent, VisionAgent, etc.) using the A2A protocol.
    # 5. Optionally, extract additional metadata such as dependencies, build tools, CI/CD config, and code quality metrics.
    # 6. Support multi-language and monorepo detection, and flag unusual or advanced repo patterns.
    # 7. Provide recommendations for README focus areas based on repo analysis (e.g., highlight API docs, setup complexity, or security features).
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add static analysis for code quality and documentation coverage.
    # - Detect presence of Docker, CI/CD, and deployment scripts.
    # - Extract and summarize API endpoints if present (REST, GraphQL, etc.).
    # - Identify and summarize test coverage and test frameworks.
    # - Suggest badges (build, coverage, license) for README.
    # - Output a JSON summary for downstream agents to use programmatically.
    # - Support for private repos and authentication.
    # - Detect and summarize security policies or contributing guidelines.
    #
    def __init__(self):
        pass

    def clone_repo(self, github_url):
        try:
            tmp_dir = tempfile.mkdtemp()
            Repo.clone_from(github_url, tmp_dir)
            return tmp_dir
        except Exception as e:
            raise Exception(f"Failed to clone repo: {e}")

    def extract_structure(self, path):
        structure = []
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = '  ' * level
            structure.append(f"{indent}- {os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for f in files:
                structure.append(f"{subindent}- {f}")
        return "\n".join(structure)

    def detect_languages(self, path):
        ext_count = {}
        for root, _, files in os.walk(path):
            for file in files:
                ext = os.path.splitext(file)[-1]
                ext_count[ext] = ext_count.get(ext, 0) + 1

        top_exts = sorted(ext_count.items(), key=lambda x: x[1], reverse=True)[:5]
        return ", ".join([f"{ext}: {count}" for ext, count in top_exts if ext])


    def extract_dependencies(self, path):
        """Extract dependencies from requirements.txt, package.json, or pyproject.toml."""
        deps = []
        for root, _, files in os.walk(path):
            for file in files:
                if file == 'requirements.txt':
                    with open(os.path.join(root, file), encoding='utf-8') as f:
                        deps.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
                if file == 'package.json':
                    import json
                    with open(os.path.join(root, file), encoding='utf-8') as f:
                        pkg = json.load(f)
                        deps.extend(list(pkg.get('dependencies', {}).keys()))
                if file == 'pyproject.toml':
                    try:
                        import toml
                        with open(os.path.join(root, file), encoding='utf-8') as f:
                            pyproj = toml.load(f)
                            deps.extend(pyproj.get('project', {}).get('dependencies', []))
                    except Exception:
                        pass
        return deps

    def detect_cicd(self, path):
        """Detect CI/CD config files."""
        cicd = []
        for root, _, files in os.walk(path):
            for file in files:
                if file in ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', 'azure-pipelines.yml']:
                    cicd.append(os.path.join(root, file))
        return cicd

    def detect_docker(self, path):
        for root, _, files in os.walk(path):
            if 'Dockerfile' in files:
                return True
        return False

    def detect_badges(self, path):
        badges = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower() == 'readme.md':
                    with open(os.path.join(root, file), encoding='utf-8') as f:
                        for line in f:
                            if 'img.shields.io' in line:
                                badges.append(line.strip())
        return badges

    def detect_api_endpoints(self, path):
        # Simple heuristic: look for Flask/FastAPI/Django/Express endpoints
        endpoints = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if any(x in line for x in ['@app.route', '@router.get', '@router.post', 'add_url_rule']):
                                endpoints.append(line.strip())
                if file.endswith('.js'):
                    with open(os.path.join(root, file), encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if any(x in line for x in ['app.get(', 'app.post(', 'router.get(', 'router.post(']):
                                endpoints.append(line.strip())
        return endpoints

    def detect_tests(self, path):
        test_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.startswith('test_') or file.endswith('_test.py') or file.endswith('.spec.js'):
                    test_files.append(os.path.join(root, file))
        return test_files

    def run(self, github_url):
        local_path = self.clone_repo(github_url)
        structure = self.extract_structure(local_path)
        langs = self.detect_languages(local_path)
        dependencies = self.extract_dependencies(local_path)
        cicd = self.detect_cicd(local_path)
        docker = self.detect_docker(local_path)
        badges = self.detect_badges(local_path)
        api_endpoints = self.detect_api_endpoints(local_path)
        tests = self.detect_tests(local_path)

        summary = f"""Repository structure:
{structure}

Detected languages:
{langs}

Dependencies: {', '.join(dependencies) if dependencies else 'None found'}
CI/CD: {', '.join(cicd) if cicd else 'None found'}
Docker: {'Yes' if docker else 'No'}
Badges: {', '.join(badges) if badges else 'None found'}
API Endpoints: {', '.join(api_endpoints) if api_endpoints else 'None found'}
Test files: {', '.join(tests) if tests else 'None found'}
"""

        message = A2AMessage(
            from_agent="AnalyzerAgent",
            to_agent="WriterAgent",
            message_type="repo_summary",
            content=summary
        )
        return message
