import streamlit as st
import openai
import time

st.title("🤖 GPT-4.1-mini Chat - 과제 1")

# API 키 입력
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are an assistant who provides precise, accurate, and relevant answers to user questions. When asked for specific facts (such as the length of an elephant's trunk), you should provide clear, factual, and concise responses. Avoid giving generic or unrelated information unless the user explicitly asks for a fun fact or additional context.",
            model="gpt-4.1-mini"
        )
        return assistant.id

    @st.cache_data
    def create_thread():
        thread = openai.beta.threads.create()
        return thread.id

    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = create_thread()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # 사용자 입력창
    st.text_input("Your question:", key="user_input")

    if st.button("Send") and st.session_state.user_input.strip():
        user_input = st.session_state.user_input.strip()
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 메시지 보내기
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # Assistant 실행
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id,
        )

        with st.spinner("Waiting for response..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("Run failed.")
                    break
                time.sleep(1)

        # 응답 받아오기
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.session_state.messages.append({"role": "assistant", "content": msg.content[0].text.value})
                break

        # 입력창 초기화
        st.session_state.user_input = ""

    # 메시지 출력
    for msg in st.session_state.messages:
        speaker = "🧑‍💻 You" if msg["role"] == "user" else "🤖 GPT"
        st.markdown(f"**{speaker}:** {msg['content']}")
else:
    st.info("API Key를 입력하면 질문을 보낼 수 있어요.")
