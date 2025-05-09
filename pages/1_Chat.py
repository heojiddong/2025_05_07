import streamlit as st
import openai
import time

st.title("🤖 GPT-4.1-mini Chat")

# API Key 입력
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# 대화 저장소
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions=(
                "You are a helpful and precise assistant. "
                "Give accurate, clear answers and avoid repeating general greetings."
            ),
            model="gpt-4.1-mini"
        )
        return assistant.id

    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()

    # Clear 버튼
    if st.button("Clear"):
        st.session_state.messages = []

    # 사용자 입력
    user_input = st.chat_input("Your question:")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # ❗ 질문마다 새 Thread 생성
        thread = openai.beta.threads.create()
        thread_id = thread.id

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=st.session_state.assistant_id,
        )

        with st.spinner("Waiting for response..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("Run failed.")
                    break
                time.sleep(1)

        # 응답 받아오기
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                assistant_response = msg.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                break

    # 💬 채팅 메시지 출력
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    st.info("Please enter your OpenAI API key to start chatting.")
