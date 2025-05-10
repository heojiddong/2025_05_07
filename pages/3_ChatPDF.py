import streamlit as st
import openai
import time

st.title("📄 ChatPDF - PDF 기반 챗봇")

# 상태 초기화
if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_visible" not in st.session_state:
    st.session_state.pdf_chat_visible = False

if "pdf_file_id" not in st.session_state:
    st.session_state.pdf_file_id = None

# ✅ API 키 입력되어 있어야 작동
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 📁 PDF 업로드
    uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

    if uploaded_file:
        with st.spinner("파일 업로드 중..."):
            file = openai.files.create(
                file=uploaded_file,
                purpose="assistants"
            )
            st.session_state.pdf_file_id = file.id
            st.success("PDF 파일 업로드 및 벡터화 완료!")

        # 어시스턴트 생성 (PDF 파일 포함)
        @st.cache_data
        def create_pdf_assistant(file_id):
            assistant = openai.beta.assistants.create(
                name="PDF Chat Assistant",
                instructions="Answer questions based only on the uploaded PDF file.",
                model="gpt-4-1106-preview",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": []}},
                file_ids=[file_id]
            )
            return assistant.id

        if "pdf_assistant_id" not in st.session_state:
            st.session_state.pdf_assistant_id = create_pdf_assistant(st.session_state.pdf_file_id)

    # 🧹 Clear 버튼
    if st.button("Clear"):
        if st.session_state.pdf_file_id:
            try:
                openai.files.delete(st.session_state.pdf_file_id)
                st.success("PDF 파일 삭제 완료")
            except Exception as e:
                st.warning("파일 삭제 실패: " + str(e))
        st.session_state.pdf_file_id = None
        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False
        st.session_state.pdf_assistant_id = None

    # 채팅 입력창
    user_input = st.chat_input("PDF 파일 내용을 기반으로 질문해보세요.")

    if user_input and st.session_state.pdf_file_id:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
            file_ids=[st.session_state.pdf_file_id]
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.pdf_assistant_id
        )

        with st.spinner("GPT가 PDF를 분석 중입니다..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("실행 실패")
                    break
                time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                reply = msg.content[0].text.value
                st.session_state.pdf_chat_messages.append({"role": "assistant", "content": reply})
                break

        st.session_state.pdf_chat_visible = True

    # 💬 채팅 출력
    if st.session_state.pdf_chat_visible:
        for msg in st.session_state.pdf_chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

else:
    st.error("❌ API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
