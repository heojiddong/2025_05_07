import streamlit as st
import openai
import time

# 제목
st.title("🤖 Chat with GPT-4.1-mini")

# 🔑 API Key가 세션에 있는지 확인
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("Please enter your API key in the Home page first.")
else:
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

    # 사용자 입력 받기
    user_input = st.text_input("Your message:")
    submit_button = st.button("Send")

    if submit_button and user_input:
        # 사용자 메시지 전송
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
        with st.spinner("Assistant is thinking..."):
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
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.write(f"**GPT:** {msg.content[0].text.value}")
                break
