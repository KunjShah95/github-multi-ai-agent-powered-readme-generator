from core.adk_agent import ADK
from core.a2a_protocol import A2AMessage


class FeedbackAgent(ADK):

    # --- AGENT ROLE PROMPT ---
    # You are the FeedbackAgent. Your role is to:
    # 1. Receive user feedback and the current README draft.
    # 2. Analyze the feedback and update the README accordingly, ensuring clarity, correctness, and user satisfaction.
    # 3. Maintain the original structure and formatting unless feedback requests otherwise.
    # 4. Optionally suggest improvements or highlight unclear feedback for user clarification.
    # 5. Support iterative feedback cycles, tracking changes and rationale.
    # 6. Optionally summarize the impact of feedback and changes made.
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add feedback history and change tracking.
    # - Support for multi-user feedback and consensus building.
    # - Integrate with issue trackers to link feedback to issues/PRs.
    # - Provide suggestions for unclear or conflicting feedback.
    # - Allow feedback on specific README sections.
    # - Output a changelog of README edits.
    #
    def __init__(self):
        super().__init__()

    def build_feedback_prompt(self, original_readme: str, user_feedback: str) -> str:
        return f"""
You are an AI README editor. Your task is to update the original README based on the user's feedback.

**Original README:**
{original_readme}

**User Feedback:**
{user_feedback}

**Instructions:**
1.  **Analyze the user's feedback** to understand the requested changes. The feedback may be a direct edit or a comment.
2.  **Incorporate the feedback** into the original README to improve its clarity, correctness, and usefulness.
3.  **Maintain the original structure and formatting** of the README as much as possible.
4.  **Do not add any new information** that is not present in the original README or the user's feedback.
5.  **Output the final, updated README.**
"""

    def run(self, feedback_text: str, previous_msg: A2AMessage):
        if previous_msg.message_type not in ["readme_draft", "readme_with_vision"]:
            return A2AMessage(
                from_agent="FeedbackAgent",
                to_agent="UI",
                message_type="error",
                content="Expected a previous README message."
            )

        prompt = self.build_feedback_prompt(previous_msg.content, feedback_text)
        updated_readme = self.generate(prompt)

        return A2AMessage(
            from_agent="FeedbackAgent",
            to_agent="ExportAgent",
            message_type="final_readme",
            content=updated_readme
        )
