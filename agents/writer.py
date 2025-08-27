from core.adk_agent import ADK
from core.a2a_protocol import A2AMessage

class WriterAgent(ADK):

    # --- AGENT ROLE PROMPT ---
    # You are the WriterAgent. Your role is to:
    # 1. Receive repository analysis and metadata from AnalyzerAgent and other sources.
    # 2. Generate a high-quality, comprehensive, and developer-friendly README.md file.
    # 3. Support multiple templates (Basic, Detailed, Creative) and customizable sections.
    # 4. Integrate additional information from VisionAgent (diagrams), FeedbackAgent (user edits), and ExportAgent (export requirements).
    # 5. Ensure the README is clear, well-structured, and follows best practices for open-source documentation.
    # 6. Optionally generate badges, code snippets, and dynamic content based on repo features.
    # 7. Support multi-language and monorepo documentation.
    # 8. Output both markdown and optionally HTML/PDF versions.
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add badge generation (build, coverage, license, etc.).
    # - Support for auto-generating API documentation sections.
    # - Integrate with code analysis tools for dynamic usage examples.
    # - Provide a README preview and linting for markdown quality.
    # - Allow user to select or customize templates and sections interactively.
    # - Support for internationalization (i18n) of README content.
    # - Output a summary of README improvements over previous versions.
    #
    def __init__(self):
        super().__init__()


    def build_prompt(self, repo_summary: str, customizations: dict) -> str:
        template = customizations.get("template", "Basic")
        sections = customizations.get("sections", [])

        prompt = f"""
You are an expert open-source documentation AI. Generate a world-class, project-specific, and visually appealing README.md for a GitHub repository, using the following detailed analysis:

{repo_summary}

**Instructions:**
1. Use all available metadata (structure, languages, dependencies, CI/CD, Docker, badges, API endpoints, test files, etc.) to infer the project's purpose, features, and best practices.
2. Generate a README.md with the following (include only if in the list of sections to include: {', '.join(sections)}):
    * **Project Title**: A clear, catchy title.
    * **Badges**: Add relevant badges (build, coverage, license, Docker, etc.) at the top.
    * **Description**: A detailed, engaging description of the project, its features, and its unique value.
    * **Table of Contents**: If the README is long, add a ToC.
    * **Installation**: Step-by-step setup instructions, including dependencies, Docker, and CI/CD if present.
    * **Usage**: Usage examples, code snippets, and API endpoint documentation if detected.
    * **Contributing**: Clear guidelines for contributors, referencing test files and CI/CD if present.
    * **License**: The project's license info.
    * **Additional Sections**: Add sections for FAQ, Troubleshooting, or Security if relevant.
3. For the template "Detailed", use emojis, badges, and clear markdown headings. For "Creative", use a unique, visually appealing layout. For "Basic", keep it simple but informative.
4. If API endpoints are detected, auto-generate an API Reference section with endpoint details and example requests.
5. If Docker is present, add a Docker usage section.
6. If CI/CD is present, mention the workflow and how to use it.
7. If test files are present, add a Testing section with instructions.
8. Use markdown best practices for formatting, accessibility, and readability.
9. Make the README stand out and be more useful than a generic template.
"""
        return prompt

    def run(self, incoming_message: A2AMessage, customizations: dict):
        if incoming_message.message_type != "repo_summary":
            return A2AMessage(
                from_agent="WriterAgent",
                to_agent="UI",
                message_type="error",
                content="WriterAgent only handles 'repo_summary' messages."
            )

        prompt = self.build_prompt(incoming_message.content, customizations)
        readme_text = self.generate(prompt)

        return A2AMessage(
            from_agent="WriterAgent",
            to_agent="VisionAgent",
            message_type="readme_draft",
            content=readme_text
        )
