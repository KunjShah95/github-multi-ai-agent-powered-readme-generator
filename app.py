
# --- Redesigned UI/UX ---
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from agents.analyzer import AnalyzerAgent
from agents.writer import WriterAgent
from agents.vision import VisionAgent
from agents.feedback import FeedbackAgent
from agents.exporter import ExportAgent
from agents.push_to_github import GitHubPushAgent
import os

analyzer = AnalyzerAgent()
writer = WriterAgent()
vision = VisionAgent()
feedback = FeedbackAgent()
exporter = ExportAgent()
github_token = os.getenv("GITHUB_TOKEN")
pusher = GitHubPushAgent(github_token)

st.set_page_config(page_title="AI README Generator", layout="wide")


# Improved sidebar (navbar) visibility with better contrast
st.markdown("""
<style>
.main {background-color: #f8fafc;}
.stButton>button {background: linear-gradient(90deg,#6366f1,#60a5fa); color: white; font-weight: 600; border-radius: 8px;}
.stTextInput>div>input, .stTextArea>div>textarea {border-radius: 8px;}
section[data-testid="stSidebar"] {
    background: #23272f !important;
    color: #fff !important;
}
.stSidebar, .stSidebarContent, .stSidebar .stHeader, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stSelectbox, .stSidebar .stButton, .stSidebar .stExpander {
    color: #fff !important;
}
.stSidebar .stTextInput>div>input, .stSidebar .stTextArea>div>textarea {
    background: #2d323b !important;
    color: #fff !important;
    border-radius: 8px;
}
.stSidebar .stButton>button {
    background: linear-gradient(90deg,#6366f1,#60a5fa);
    color: #fff;
    font-weight: 600;
    border-radius: 8px;
}
.stMarkdown code {background: #f3f4f6; color: #0f172a;}
.stAlert {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Multi-Agent GitHub README Generator")
st.caption("Generate beautiful, smart READMEs for any GitHub repo using a team of AI agents.")

if 'global_state' not in st.session_state:
    st.session_state['global_state'] = {}

with st.sidebar:
    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=60)
    st.header("1️⃣ Repository")
    github_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo", help="Paste the public GitHub repository URL.")
    image_file = st.file_uploader("Optional System Diagram", type=["png", "jpg", "jpeg"], help="Upload a diagram to enhance the README.")
    st.header("2️⃣ Customization")
    readme_template = st.selectbox("README Template", ["Basic", "Detailed", "Creative"], help="Choose the style of README.")
    with st.expander("Sections to Include", expanded=True):
        include_sections = {
            "Installation": st.checkbox("Installation", True, help="How to install the project."),
            "Usage": st.checkbox("Usage", True, help="How to use the project."),
            "Contributing": st.checkbox("Contributing", True, help="How to contribute."),
            "License": st.checkbox("License", True, help="Project license info."),
        }
    st.header("3️⃣ Actions")
    gen_btn = st.button("🚀 Generate README", use_container_width=True)
    st.divider()
    st.header("4️⃣ Feedback & Export")
    feedback_text = st.text_area("Feedback or Edit", help="Suggest improvements or edit the README.")
    regen_btn = st.button("🔁 Regenerate with Feedback", use_container_width=True)
    export_btn = st.button("💾 Export Final README", use_container_width=True)
    push_btn = st.button("🚀 Push to GitHub", use_container_width=True)

# --- Progress Bar ---
progress_steps = ["Analyze Repo", "Generate README", "Vision (Optional)", "Feedback", "Export/Push"]
progress = 0
if 'final_readme' in st.session_state['global_state']:
    progress = 4
elif 'writer_msg' in st.session_state['global_state']:
    progress = 2
elif 'analyzer_msg' in st.session_state['global_state']:
    progress = 1
st.progress(progress/4, text=f"Step {progress+1}: {progress_steps[progress]}")

st.markdown("---")
cols = st.columns([2, 1])

with cols[0]:
    st.subheader("📄 Live README Preview")
    readme_output = st.empty()
    if 'final_readme' in st.session_state['global_state']:
        readme_content = st.session_state['global_state']['final_readme']
        readme_output.markdown(readme_content, unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download README.md",
            data=readme_content,
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.info("Generate a README to see the preview here.")
with cols[1]:
    st.subheader("🧩 Pipeline Status")
    st.markdown("""
    <ul style='font-size:1.1em;'>
    <li>🔍 <b>Analyze Repo</b>: {}</li>
    <li>✍️ <b>Generate README</b>: {}</li>
    <li>🖼️ <b>Vision (Optional)</b>: {}</li>
    <li>📝 <b>Feedback</b>: {}</li>
    <li>📤 <b>Export/Push</b>: {}</li>
    </ul>
    """.format(
        "✅" if 'analyzer_msg' in st.session_state['global_state'] else "⬜",
        "✅" if 'writer_msg' in st.session_state['global_state'] else "⬜",
        "✅" if 'vision_msg' in st.session_state['global_state'] else "⬜",
        "✅" if 'final_readme' in st.session_state['global_state'] and feedback_text else "⬜",
        "✅" if 'final_readme' in st.session_state['global_state'] else "⬜"
    ), unsafe_allow_html=True)

# --- Main Actions ---
if gen_btn:
    if github_url:
        with st.spinner("Analyzing repository and generating README..."):
            try:
                analysis_msg = analyzer.run(github_url)
                st.session_state['global_state']["analyzer_msg"] = analysis_msg
                customizations = {
                    "template": readme_template,
                    "sections": [section for section, included in include_sections.items() if included]
                }
                readme_msg = writer.run(analysis_msg, customizations)
                st.session_state['global_state']["writer_msg"] = readme_msg
                if image_file:
                    vision_msg = vision.run(image_file, readme_msg)
                    st.session_state['global_state']["vision_msg"] = vision_msg
                    st.session_state['global_state']['final_readme'] = vision_msg.content
                else:
                    st.session_state['global_state']['final_readme'] = readme_msg.content
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid GitHub URL.")

if regen_btn:
    if 'final_readme' in st.session_state['global_state'] and feedback_text:
        with st.spinner("Applying feedback and regenerating README..."):
            prev_msg_content = st.session_state['global_state']['final_readme']
            from core.a2a_protocol import A2AMessage
            prev_msg = A2AMessage("UI", "FeedbackAgent", "final_readme", prev_msg_content)
            feedback_msg = feedback.run(feedback_text, prev_msg)
            st.session_state['global_state']['final_readme'] = feedback_msg.content
            st.rerun()
    else:
        st.warning("Generate a README first and provide feedback.")

if export_btn:
    if 'final_readme' in st.session_state['global_state']:
        from core.a2a_protocol import A2AMessage
        final_msg = A2AMessage("UI", "ExportAgent", "final_readme", st.session_state['global_state']['final_readme'])
        export_msg = exporter.run(final_msg)
        st.success(export_msg.content)
    else:
        st.warning("No final README to export.")

if push_btn:
    if 'final_readme' in st.session_state['global_state'] and github_url:
        with st.spinner("Pushing README to GitHub..."):
            from core.a2a_protocol import A2AMessage
            final_msg = A2AMessage("UI", "GitHubPushAgent", "final_readme", st.session_state['global_state']['final_readme'])
            response = pusher.run(github_url, final_msg)
            st.info(response.content)
    else:
        st.warning("No final README to push or GitHub URL provided.")
