import streamlit as st

def display_writing_studio(client):
    """
    Displays the AI Writing and Tone Refinement Studio section.
    """
    st.subheader("✍️ AI Writing & Tone Refinement Studio")
    st.info("Draft, edit, and fine-tune your text by selecting the desired tone and action.")

    # --- Session State Initialization for this section ---
    st.session_state.setdefault("studio_messages", [
        {"role": "assistant", "content": "Hello! Provide your draft or a prompt, and let's define the style you need."}
    ])
    st.session_state.setdefault("input_text", "")
    
    # --- Control Panel (Input and Constraints) ---
    with st.container():
        st.markdown("#### 📝 Input & Constraints")
        
        # Text Area for Input
        input_text = st.text_area(
            "Enter your text or writing prompt here:",
            height=150,
            key="studio_input_area",
            placeholder="E.g., Write a persuasive email to clients announcing a price increase."
        )
        st.session_state["input_text"] = input_text

        col1, col2, col3 = st.columns(3)
        
        with col1:
            tone = st.selectbox(
                "Target Tone",
                options=["Formal", "Casual", "Urgent", "Persuasive", "Humorous", "Academic", "Concise", "Friendly"],
                key="tone_selector"
            )

        with col2:
            action = st.selectbox(
                "Desired Action",
                options=["Generate Content", "Refine Tone", "Summarize Text"],
                key="action_selector"
            )
            
        with col3:
            audience = st.text_input(
                "Target Audience (e.g., Executives, Students)",
                value="General Audience",
                key="audience_input"
            )

    st.markdown("---")
    
    # --- Action Button ---
    if st.button(f"✨ Run AI: {action}", use_container_width=True, key="run_ai_button"):
        if not st.session_state["input_text"].strip():
            st.warning("Please enter some text or a prompt to analyze.")
        else:
            # Append user request to chat history
            user_prompt = f"ACTION: {action}\nTONE: {tone}\nAUDIENCE: {audience}\nINPUT: {st.session_state['input_text'][:100]}..."
            st.session_state["studio_messages"].append({"role": "user", "content": user_prompt})
            
            # Simulate the AI task execution (Placeholder for Gemini API call)
            # The actual API call would use the defined tone and audience as part of the system prompt
            with st.spinner(f"✍️ Running AI to {action.lower()} in a {tone} tone..."):
                
                # --- Placeholder for Gemini API Call ---
                # Example system prompt construction:
                # system_prompt = f"You are a professional editor. Your task is to {action.lower()} the provided text to be {tone} for a {audience} audience."
                # response = stream_gemini_response(client, system_prompt + input_text)
                
                simulated_response = (
                    f"**AI Result ({action} | {tone} Tone):**\n\n"
                    f"*(Placeholder: In the real app, the Gemini model would generate the content here, "
                    f"tailored to the constraints.)*\n\n"
                    f"**Your Request:** Please {action.lower()} the following text in a {tone} tone for a {audience} audience: "
                    f"\"{st.session_state['input_text'].strip()}\""
                )
                response = simulated_response

            # Display and save the response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state["studio_messages"].append({"role": "assistant", "content": response})

    st.markdown("---")
    
    # --- Chat History Display ---
    st.markdown("#### 💬 Output History")
    for msg in reversed(st.session_state["studio_messages"]):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
