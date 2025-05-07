import streamlit as st
import openai
import time

st.title("GPT-4.1-mini 챗봇")

# 🔐 OpenAI API Key 입력 받기 및 session_state 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_input = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_input

# API Key 설정
if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 캐시된 assistant 생성 함수
    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are a helpful assistant.",
            model="gpt-4-1106-preview"
        )
        return assistant.id

    # 캐시된 쓰레드 생성 함수
    @st.cache_data
    def create_thread():
        thread = openai.beta.threads.create()
        return thread.id

    # 세션 상태에 저장
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = create_thread()

    # 사용자 질문 입력
    user_input = st.text_input("Your question:")
    send_button = st.button("Send")

    if send_button and user_input:
        # 질문 추가
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # 응답 생성 요청
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id,
        )

        # 상태 확인
        with st.spinner("GPT가 생각 중..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("GPT 응답 실패!")
                    break
                time.sleep(1)

        # 최신 메시지만 출력
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.success("GPT 응답:")
                st.write(msg.content[0].text.value)
                break  # 최신 assistant 메시지만 출력

else:
    st.info("먼저 OpenAI API Key를 입력하세요.")
