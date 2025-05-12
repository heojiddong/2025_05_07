import streamlit as st
import openai
import PyPDF2

st.title("📄 ChatPDF - File Search 기반 PDF 챗봇")

# 상태 초기화
if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_visible" not in st.session_state:
    st.session_state.pdf_chat_visible = False

# ✅ API 키 필요
if "api_key" in st.session_state and st.session_state.api_key:
    openai.api_key = st.session_state.api_key

    # 🧹 Clear 버튼
    if st.button("🧹 Clear"):
        st.session_state.pdf_chat_messages = []
        st.session_state.pdf_chat_visible = False
        st.success("초기화 완료")

    # 📁 PDF 업로드 및 텍스트 추출
    uploaded_file = st.file_uploader("PDF 파일 업로드", type="pdf")
    if uploaded_file:
        with st.spinner("PDF 분석 중..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()

            if not pdf_text:
                st.error("PDF에서 텍스트를 추출할 수 없습니다. 파일을 확인해주세요.")
            else:
                st.session_state.pdf_text = pdf_text
                st.success("PDF 분석 완료!")

    # 💬 질문 입력
    user_input = st.text_input("PDF 내용을 기반으로 질문해보세요.")
    if user_input and 'pdf_text' in st.session_state:
        st.session_state.pdf_chat_messages.append({"role": "user", "content": user_input})

        try:
            # 최신 OpenAI API 방식으로 질문 처리
            response = openai.chat_completions.create(  # chat_completions.create() 사용
                model="gpt-4",  # GPT-4 모델 사용
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": st.session_state.pdf_text}
                ]
            )

            reply = response['choices'][0]['message']['content'].strip()  # 'choices[0]['message']['content']로 수정
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
