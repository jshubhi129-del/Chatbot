import google.generativeai as genai

genai.configure(api_key="your API key")  # Replace with your API key

model = genai.GenerativeModel("gemini-1.5-flash")  # Using Gemini AI

def askai(user_prompt):
    try:
        response = model.generate_content(user_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error in AI response: {e}"
