import streamlit as st
import openai
import time

st.title("💬 GPT-4.1-mini Chat - 과제 2")

# 🔒 메시지 및 화면 표시 여부 초기화
if "chat2_messages" not in st.session_state:
    st.session_state.chat2_messages = []

if "chat2_visible" not in st.session_state:
    st.session_state.chat2_visible = False  # 기본은 대화 숨김

# ✅ API 키가 세션에 있어야 사용 가능
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # Assistant 생성
    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are a helpful and accurate assistant. Give direct, fact-based, and concise answers.",
            model="gpt-4.1-mini"
        )
        return assistant.id

    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()

    # 🔘 Clear 버튼
    if st.button("🧹 Clear Chat"):
        st.session_state.chat2_messages = []
        st.session_state.chat2_visible = False

    # 💬 사용자 입력
    user_input = st.chat_input("Type your message...")

    if user_input:
        # 메시지 저장
        st.session_state.chat2_messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        # 매번 새 Thread 생성
        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # 실행
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.assistant_id,
        )

        # 응답 대기
        with st.spinner("GPT is thinking..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("Run failed.")
                    break
                time.sleep(1)

        # 응답 받기
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                reply = msg.content[0].text.value
                st.session_state.chat2_messages.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").markdown(reply)
                break

        # 이제부터 대화 출력 허용
        st.session_state.chat2_visible = True

    # 🔽 이전 대화 출력 (단, visible일 때만)
    if st.session_state.chat2_visible:
        for msg in st.session_state.chat2_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

else:
    st.error("❌ API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
