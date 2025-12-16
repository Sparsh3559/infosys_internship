import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

st.title("AI System for Personalized Content Creation")
st.write("Streamlit app is running successfully")
st.divider()

prompt = st.text_input("Enter your prompt")

st.divider()

content_type = st.selectbox(
    "Select content type",
    ["LinkedIn Post", "Email", "Advertisement", "Conversation"]
)

llm = ChatOpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    temperature=0.5
)

templates = {
    "LinkedIn Post": "Write a professional LinkedIn post about: {topic}",
    "Email": "Write a professional email about: {topic}",
    "Advertisement": "Write a short advertisement copy about: {topic}",
    "Conversation": "Write a friendly conversational response about: {topic}"
}

if prompt:
    st.balloons()

    prompt_template = PromptTemplate(
        input_variables=["topic"],
        template=templates[content_type]
    )

    final_prompt = prompt_template.format(topic=prompt)

    with st.spinner("Generating content..."):
        response = llm.invoke(final_prompt)

    st.subheader("Generated Content")
    st.write(response.content)