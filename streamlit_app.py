import streamlit as st
import openai
import time

st.title("🤖 GPT-4.1-mini Chat - 과제 1")

# 🔑 API Key 입력
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    @st.cache_data
    def create_assistant():
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are an assistant who provides factual, specific answers to user questions. Keep answers clear and on-topic.",
            model="gpt-4.1-mini"
        )
        return assistant.id

    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = create_assistant()

    # --- 입력 Form ---
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your question:")
        submitted = st.form_submit_button("Send")

    if submitted and user_input.strip():
        # 🔄 새로운 쓰레드 생성
        thread = openai.beta.threads.create()
        thread_id = thread.id

        # 질문 저장
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        # 메시지 보내기
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input.strip()
        )

        # 실행 요청
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # 응답 대기
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

        # 응답 메시지 가져오기
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                answer = msg.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": answer})
                break

    # 🔁 대화 출력
    for msg in st.session_state.messages:
        speaker = "🧑‍💻 You" if msg["role"] == "user" else "🤖 GPT"
        st.markdown(f"**{speaker}:** {msg['content']}")
else:
    st.info("API Key를 입력하면 시작할 수 있어요.")
