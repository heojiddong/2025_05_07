import streamlit as st
import openai
import time

st.title("📄 ChatPDF - PDF 기반 챗봇")

# 세션 상태 초기화
if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_visible" not in st.session_state:
    st.session_state.pdf_chat_visible = False

if "pdf_file_id" not in st.session_state:
    st.session_state.pdf_file_id = None

if "pdf_assistant_id" not in st.session_state:
    st.session_state.pdf_assistant_id = None

if "pdf_vector_store_id" not in st.session_state:
    st.session_state.pdf_vector_store_id = None

# ✅ API 키 필요
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 🧹 Clear 버튼: PDF, Assistant, Vector Store, 채팅 모두 삭제
    if st.button("🧹 Clear"):
        errors = []

        # PDF 파일 삭제
        if st.session_state.pdf_file_id:
            try:
                openai.files.delete(st.session_state.pdf_file_id)
            except Exception as e:
                errors.append(f"PDF 삭제 실패: {str(e)}")
            st.session_state.pdf_file_id = None

        # Assistant 삭제
        if st.session_state.pdf_assistant_id:
            try:
                openai.beta.assistants.delete(st.session_state.pdf_assistant_id)
            except Exception as e:
                errors.append(f"Assistant 삭제 실패: {str(e)}")
            st.session_state.pdf_assistant_id = None

        # Vector Store 삭제
        if st.session_state.pdf_vector_store_id:
            try:
                openai.beta.vector_stores.delete(st.session_state.pdf_vector_store_id)
            except Exception as e:
                errors.append(f"Vector Store 삭제 실패: {str(e)}")
            st.session_state.pdf_vector_store_id = None

        # 채팅 초기화
        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False

        if errors:
            st.warning("일부 항목 삭제 실패:\n" + "\n".join(errors))
        else:
            st.success("모든 정보 초기화 완료!")

    # 📁 PDF 업로드 및 Assistant + Vector Store 생성
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")
    if uploaded_file and st.session_state.pdf_file_id is None:
        with st.spinner("PDF 업로드 및 벡터 스토어 준비 중..."):
            # PDF 파일 업로드
            file = openai.files.create(file=uploaded_file, purpose="assistants")
            st.session_state.pdf_file_id = file.id

            # 벡터 스토어 생성 및 파일 연결
            vector_store = openai.beta.vector_stores.create(name="PDF Vector Store")
            st.session_state.pdf_vector_store_id = vector_store.id

            openai.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=[file.id]
            )

            # Assistant 생성 및 Vector Store 연결
            assistant = openai.beta.assistants.create(
                name="PDF Chat Assistant",
                instructions="You are a helpful assistant who only answers based on the uploaded PDF file.",
                model="gpt-4-1106-preview",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )
            st.session_state.pdf_assistant_id = assistant.id

            st.success("Assistant 및 벡터 스토어 생성 완료!")

    # 💬 질문 입력
    user_input = st.chat_input("PDF 내용을 기반으로 질문해보세요.")
    if user_input and st.session_state.pdf_assistant_id and st.session_state.pdf_file_id:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        # 쓰레드 생성
        thread = openai.beta.threads.create()

        # 사용자 메시지 추가 (attachments로 파일 연결)
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
            attachments=[
                {
                    "file_id": st.session_state.pdf_file_id,
                    "tools": [{"type": "file_search"}]
                }
            ]
        )

        # Run 실행
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.pdf_assistant_id,
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

        # 응답 받아오기
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant" and msg.content:
                try:
                    reply = msg.content[0].text.value
                    st.session_state.pdf_chat_messages.append({"role": "assistant", "content": reply})
                    break
                except Exception as e:
                    st.error(f"응답 파싱 실패: {str(e)}")
                    break

        st.session_state.pdf_chat_visible = True

    # 💬 채팅 출력
    if st.session_state.pdf_chat_visible:
        for msg in st.session_state.pdf_chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

else:
    st.error("❌ API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
