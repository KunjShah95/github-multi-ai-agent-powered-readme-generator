from core.a2a_protocol import A2AMessage
import os


class ExportAgent:

    # --- AGENT ROLE PROMPT ---
    # You are the ExportAgent. Your role is to:
    # 1. Receive the final README content from upstream agents.
    # 2. Save the README to a specified directory, ensuring correct encoding and file structure.
    # 3. Optionally export the README in multiple formats (Markdown, PDF, HTML, etc.).
    # 4. Provide status updates and file paths to the UI or next agent.
    # 5. Support versioning and backup of previous README exports.
    # 6. Optionally trigger notifications or webhooks after export.
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add export to PDF/HTML using markdown converters.
    # - Support custom export directories and filenames.
    # - Integrate with cloud storage (Google Drive, S3, etc.).
    # - Add export history and rollback capability.
    # - Optionally compress or encrypt exported files.
    # - Provide a summary report of export actions.
    #
    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)


    def save_readme(self, content: str, filename="README.md"):
        """Save README as Markdown and trigger additional export features."""
        path = os.path.join(self.export_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        # Export to other formats
        self.export_to_pdf(path)
        self.export_to_html(path)
        # Versioning
        self.save_version(path)
        # Cloud storage
        self.upload_to_cloud(path)
        # Encryption (optional)
        self.encrypt_export(path)
        # Log export
        self.log_export(path)
        # Notifications
        self.send_notification(path)
        return path

    def export_to_pdf(self, md_path):
        """Export Markdown to PDF (stub)."""
        # TODO: Use markdown2pdf or similar library
        pass

    def export_to_html(self, md_path):
        """Export Markdown to HTML (stub)."""
        # TODO: Use markdown2 or similar library
        pass

    def save_version(self, file_path):
        """Save a versioned copy of the export (stub)."""
        # TODO: Implement versioning logic (timestamped copies, etc.)
        pass

    def upload_to_cloud(self, file_path):
        """Upload export to cloud storage (stub)."""
        # TODO: Integrate with Google Drive, Dropbox, AWS S3, etc.
        pass

    def encrypt_export(self, file_path):
        """Encrypt the exported file (stub)."""
        # TODO: Use cryptography library for optional encryption
        pass

    def log_export(self, file_path):
        """Log export details (stub)."""
        # TODO: Write export details to a log file or database
        pass

    def send_notification(self, file_path):
        """Send notification after export (stub)."""
        # TODO: Integrate with email, Slack, or webhook
        pass

    def export_additional_files(self, files: list):
        """Export multiple documentation files (stub)."""
        # TODO: Support exporting more than just README.md
        pass

    def web_export_api(self):
        """Web/API interface for export management (stub)."""
        # TODO: Implement a Flask/FastAPI endpoint for export actions
        pass

    def run(self, message: A2AMessage):
        if message.message_type != "final_readme":
            return A2AMessage(
                from_agent="ExportAgent",
                to_agent="UI",
                message_type="error",
                content="Expected final_readme message."
            )

        saved_path = self.save_readme(message.content)

        return A2AMessage(
            from_agent="ExportAgent",
            to_agent="UI",
            message_type="readme_saved",
            content=f"README saved to: {saved_path}"
        )
