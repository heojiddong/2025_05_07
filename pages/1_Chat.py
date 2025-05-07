import streamlit as st
import openai
import time

# Chat 페이지 제목
st.title("🤖 GPT-4.1-mini Chat")

# 🔑 API Key 입력 및 세션에 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# API Key 입력 후 진행
if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 어시스턴트 생성 함수 (캐시)
    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are a helpful assistant.",
            model="gpt-4-1106-preview"
        )
        return assistant.id

    # 쓰레드 생성 함수 (캐시)
    @st.cache_data
    def create_thread():
        thread = openai.beta.threads.create()
        return thread.id

    # 상태 초기화
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = create_thread()

    # 대화 내용 저장
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 사용자 메시지 입력 받기
    user_input = st.chat_input("Your question:")

    # Clear 버튼
    clear_button = st.button("Clear")

    if clear_button:
        st.session_state.messages = []  # 대화 내용 초기화

    # 사용자가 메시지를 보내면
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # 실행 시작
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id,
        )

        # 응답 기다리기
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

        # 응답 가져오기
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_response = ""
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                assistant_response = msg.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                break

    # 대화 내용 표시 (채팅 형식)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])

else:
    st.info("Please enter your OpenAI API key to start chatting.")
