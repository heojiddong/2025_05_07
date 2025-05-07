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

    # 입력값 초기화용 변수
    if "last_sent" not in st.session_state:
        st.session_state.last_sent = ""

    # 사용자 입력
    user_input = st.text_input("Your question:", value=st.session_state.last_sent, key="user_input_{}".format(time.time()))  # key에 시간을 추가하여 매번 새로 고침

    if st.button("Send") and user_input:
        st.session_state.last_sent = user_input  # 사용자 입력 저장

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

        # 입력창 비우기
        st.session_state.last_sent = ""  # 질문 입력칸을 비워줍니다.

        # 입력칸을 빈 값으로 리셋하기 위해서 새로고침을 강제
        st.experimental_rerun()  # 새로운 요청에 대해 페이지를 다시 로드하여 입력칸을 비웁니다.
else:
    st.info("API Key를 입력하면 질문을 보낼 수 있어요.")
