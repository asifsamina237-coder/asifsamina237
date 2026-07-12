import streamlit as st
import openai
import json
from PIL import Image
import pandas as pd
import io
import base64

st.set_page_config(page_title="ReceiptAI - Smart Expense Tracker", layout="wide")

st.title("📄 ReceiptAI Dashboard")
st.subheader("Automate your business expenses instantly with AI")

st.sidebar.header("💳 Subscription & Settings")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("👑 Premium Access")

STRIPE_LINK = "https://stripe.com"

has_paid = st.sidebar.checkbox("🔓 I have a Premium Active Subscription", value=False)

if not has_paid:
    st.sidebar.markdown(f'''
        <a href="{STRIPE_LINK}" target="_blank">
            <button style="
                background-color: #FF4B4B;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                width: 100%;
                font-weight: bold;">
                💳 Subscribe for $29/Month
            </button>
        </a>
    ''', unsafe_html=True)
    st.sidebar.warning("Please subscribe above and check the box to unlock the AI Scanner.")

if has_paid:
    if not api_key:
        st.info("⚠️ Please enter an OpenAI API Key in the sidebar to test the app features.")
    else:
        openai.api_key = api_key

    st.write("### 📸 Upload Receipt or Invoice")
    uploaded_file = st.file_uploader("Choose an image file...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns()
        
        with col1:
            st.image(image, caption='Uploaded Document', use_container_width=True)
            
        with col2:
            with st.spinner("🤖 AI Agent is reading your document..."):
                try:
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    prompt_instructions = (
                        "You are an expert accountant AI. Analyze this receipt or invoice image. "
                        "Extract the details precisely and return them strictly in JSON format with these exact keys: "
                        "'vendor', 'date', 'subtotal', 'tax', 'total_amount', 'category'."
                    )

                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={ "type": "json_object" },
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_instructions},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                                ]
                            }
                        ]
                    )
                    
                    result_text = response.choices.message.content
                    extracted_data = json.loads(result_text)
                    
                    st.success("✅ Extraction Complete!")
                    st.write("### 📊 Extracted Data Details")
                    
                    df = pd.DataFrame([extracted_data])
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download as Excel/CSV File",
                        data=csv,
                        file_name="extracted_expense.csv",
                        mime="text/csv",
                    )
                    
                except Exception as e:
                    st.error(f"An processing error occurred: {str(e)}")
else:
    st.info("🔒 The dashboard is locked. Use the sidebar to activate premium access.")
