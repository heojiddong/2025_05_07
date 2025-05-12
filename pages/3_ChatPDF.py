import streamlit as st
import openai
import time

st.title("📄 ChatPDF - File Search 기반 PDF 챗봇")

# 상태 초기화
if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_visible" not in st.session_state:
    st.session_state.pdf_chat_visible = False

if "pdf_file_id" not in st.session_state:
    st.session_state.pdf_file_id = None

if "pdf_assistant_id" not in st.session_state:
    st.session_state.pdf_assistant_id = None

# ✅ API 키 필요
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 🧹 Clear 버튼
    if st.button("🧹 Clear"):
        try:
            if st.session_state.pdf_file_id:
                openai.File.delete(st.session_state.pdf_file_id)
                st.session_state.pdf_file_id = None
        except Exception as e:
            st.warning(f"파일 삭제 실패: {str(e)}")

        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False
        st.session_state.pdf_assistant_id = None
        st.success("초기화 완료")

    # 📁 PDF 업로드 및 Assistant 생성
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")
    if uploaded_file and st.session_state.pdf_file_id is None:
        with st.spinner("PDF 업로드 중..."):
            file = openai.File.create(file=uploaded_file, purpose="answers")
            st.session_state.pdf_file_id = file.id

            st.success("PDF 파일 업로드 완료!")

    # 💬 질문 입력
    user_input = st.text_input("PDF 내용을 기반으로 질문해보세요.")
    if user_input and st.session_state.pdf_file_id:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        try:
            # 최신 OpenAI API 방식으로 질문 처리
            response = openai.ChatCompletion.create(
                model="gpt-4",  # GPT-4 모델 사용
                messages=[{"role": "system", "content": "You are a helpful assistant who answers based on the uploaded PDF."},
                          {"role": "user", "content": user_input}],
                documents=[st.session_state.pdf_file_id]  # PDF 파일로부터 정보 추출
            )

            reply = response['choices'][0]['message']['content'].strip()
            st.session_state.pdf_chat_messages.append({"role": "assistant", "content": reply})
            st.session_state.pdf_chat_visible = True
        except Exception as e:
            st.error(f"응답 실패: {str(e)}")

    # 💬 대화 출력
    if st.session_state.pdf_chat_visible:
        for msg in st.session_state.pdf_chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

else:
    st.error("❌ API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
