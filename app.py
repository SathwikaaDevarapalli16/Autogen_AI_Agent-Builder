
import streamlit as st
import os
import pandas as pd
from autogen import UserProxyAgent, GroupChat, GroupChatManager
from agents import get_agents

# Load API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set it in environment variables.")
    st.stop()

# Agent configuration
config = {
    "config_list": [{"model": "gpt-3.5-turbo", "api_key": OPENAI_API_KEY}],
    "temperature": 0.7,
}

st.set_page_config(page_title="Startup Builder AI", layout="wide")
st.title("🚀 AI Startup Builder (AutoGen Multi-Agent)")

# User prompt
startup_idea = st.text_area(
    "Describe your startup idea:",
    height=150,
    placeholder="Ex: I want to build a startup around Ayurvedic protein powders for gamers..."
)

if st.button("Build My Startup") and startup_idea.strip():
    with st.spinner("🤖 Agents are working..."):

        # Create agents
        agents = get_agents(config)
        user = UserProxyAgent(name="User", code_execution_config=False)
        groupchat = GroupChat(agents=[user] + agents, messages=[], max_round=12)
        manager = GroupChatManager(groupchat=groupchat, llm_config=config)

        # Start the conversation
        user.initiate_chat(manager, message=startup_idea)

        # Collect agent outputs
        agent_outputs = {}
        for msg in groupchat.messages:
            if 'sender' not in msg or 'content' not in msg:
                continue
            role = msg['sender'].replace("Agent", "").replace("Checker", " Checker").strip()
            if role not in agent_outputs:
                agent_outputs[role] = msg['content']
            else:
                agent_outputs[role] += "

" + msg['content']

    st.success("🎉 Your AI startup is ready!")

    for section, content in agent_outputs.items():
        st.subheader(f"🧠 {section}")
        # Try to parse markdown table if it exists
        if "|---" in content and "|" in content:
            try:
                table_lines = [line.strip() for line in content.splitlines() if "|" in line]
                table_text = "
".join(table_lines)
                from io import StringIO
                df = pd.read_csv(StringIO(table_text), sep="|", engine="python")
                df.columns = [col.strip() for col in df.columns]
                df = df.dropna(axis=1, how="all")
                st.dataframe(df)
            except Exception:
                st.markdown(content)
        else:
            st.markdown(content)
  