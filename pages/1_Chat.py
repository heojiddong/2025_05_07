import streamlit as st
import openai
import time

st.title("💬 GPT-4.1-mini Chat - 과제 2")

# 대화 메시지 상태
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ API 키가 존재할 경우에만 실행
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 어시스턴트 생성 (고정)
    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are a helpful and accurate assistant. Give clear, precise answers.",
            model="gpt-4.1-mini"
        )
        return assistant.id

    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()

    # 🔘 Clear 버튼
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

    # 💬 사용자 입력
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 질문마다 새로운 Thread 생성
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

        with st.spinner("GPT is typing..."):
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

        # 응답 메시지 받기
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                reply = msg.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": reply})
                break

    # 💬 대화 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

else:
    st.error("API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
