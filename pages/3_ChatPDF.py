import streamlit as st
import openai
import time
import PyPDF2

st.title("📄 ChatPDF - PDF 기반 챗봇 (로컬 분석)")

# 상태 초기화
if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_visible" not in st.session_state:
    st.session_state.pdf_chat_visible = False

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# ✅ API 키 필요
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 🧹 Clear 버튼
    if st.button("🧹 Clear"):
        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False
        st.session_state.pdf_text = ""

    # 📁 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")

    if uploaded_file is not None:
        reader = PyPDF2.PdfReader(uploaded_file)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() or ""
        st.session_state.pdf_text = extracted_text
        st.success("PDF 텍스트 추출 완료!")

    # 💬 질문 입력
    user_input = st.chat_input("PDF 내용을 기반으로 질문해보세요.")

    if user_input and st.session_state.pdf_text:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        # 시스템에 PDF 내용을 프롬프트로 넣어서 질문
        messages = [
            {"role": "system", "content": "다음 PDF 문서 내용을 참고하여 사용자 질문에 정확하게 답하세요."},
            {"role": "system", "content": st.session_state.pdf_text[:4000]},  # 길이 제한 있음
            {"role": "user", "content": user_input},
        ]

        with st.spinner("GPT가 PDF를 분석 중입니다..."):
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages
            )
            reply = response.choices[0].message.content
            st.session_state.pdf_chat_messages.append({"role": "assistant", "content": reply})
            st.session_state.pdf_chat_visible = True

    # 💬 채팅 출력
    if st.session_state.pdf_chat_visible:
        for msg in st.session_state.pdf_chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

else:
    st.error("❌ API 키가 설정되지 않았습니다. 홈 페이지에서 먼저 입력해 주세요.")
