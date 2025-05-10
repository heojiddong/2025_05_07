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

if "pdf_vector_store_id" not in st.session_state:
    st.session_state.pdf_vector_store_id = None

if "pdf_assistant_id" not in st.session_state:
    st.session_state.pdf_assistant_id = None

# ✅ API 키 필요
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # Clear 버튼
    if st.button("🧹 Clear"):
        if st.session_state.pdf_file_id:
            try:
                openai.files.delete(st.session_state.pdf_file_id)
                st.success("PDF 파일 삭제 완료")
            except Exception as e:
                st.warning("파일 삭제 실패: " + str(e))
        st.session_state.pdf_file_id = None
        st.session_state.pdf_vector_store_id = None
        st.session_state.pdf_assistant_id = None
        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False

    # 📁 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")

    if uploaded_file:
        with st.spinner("파일 업로드 중..."):
            file = openai.files.create(
                file=uploaded_file,
                purpose="assistants"
            )
            st.session_state.pdf_file_id = file.id

            # Vector store 생성
            vector_store = openai.beta.vector_stores.create(name="PDF Vector Store")
            openai.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=[file.id]
            )
            st.session_state.pdf_vector_store_id = vector_store.id

            # Assistant 생성
            assistant = openai.beta.assistants.create(
                name="PDF Chat Assistant",
                instructions="Answer questions based only on the uploaded PDF file.",
                model="gpt-4-1106-preview",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )
            st.session_state.pdf_assistant_id = assistant.id

        st.success("PDF 파일 벡터화 및 어시스턴트 생성 완료!")

    # 💬 질문 입력
    user_input = st.chat_input("PDF 내용을 기반으로 질문해보세요.")

    if user_input and st.session_state.pdf_assistant_id and st.session_state.pdf_file_id:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.pdf_assistant_id,
        )

        with st.spinner("PDF 기반 응답 생성 중..."):
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
