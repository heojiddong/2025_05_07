import streamlit as st
import openai
import time

st.title("🤖 GPT-4.1-mini Chat - 과제 1")

# 🔑 API Key 입력
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
            instructions="You are a helpful assistant.",
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

    # 입력값 초기화용 변수
    if "last_sent" not in st.session_state:
        st.session_state.last_sent = ""

    # 사용자 입력
    user_input = st.text_input("Your question:", value="", key="user_input")

    # rerun 플래그 확인
    if "do_rerun" not in st.session_state:
        st.session_state.do_rerun = False

    if st.session_state.do_rerun:
        st.session_state.do_rerun = False
        st.experimental_rerun()

    if st.button("Send") and user_input:
        st.session_state.last_sent = user_input  # 저장

        # 메시지 생성
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # 응답 실행
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

        # 응답 출력
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.write(f"**GPT:** {msg.content[0].text.value}")
                break

        # 입력창 비우기 위해 리런
        st.session_state.do_rerun = True

else:
    st.info("API Key를 입력하면 질문을 보낼 수 있어요.")
