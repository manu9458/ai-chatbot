import streamlit as st
import pandas as pd
import plotly.express as px # Import Plotly Express for plotting

def display_data_analysis():
    """
    Display the AI-Powered Data Analysis section for CSV/Excel file upload and exploration.
    This function contains the core logic for EDA using natural language and plotting UI.
    """
    st.subheader("📈 AI-Powered Data Analysis")
    st.info("Upload a CSV or Excel file and start exploring your data with chat commands or custom plots.")

    # File uploader for data
    data_file = st.file_uploader(
        "Upload a CSV or XLSX file",
        type=["csv", "xlsx"],
        key="data_uploader"
    )

    if data_file:
        # Check if a new file is uploaded or if the session state DataFrame is missing
        if "df" not in st.session_state or st.session_state.uploaded_file_name != data_file.name:
            try:
                # Read the file into a DataFrame and store in session state
                if data_file.name.endswith('.csv'):
                    df = pd.read_csv(data_file)
                else: # .xlsx
                    df = pd.read_excel(data_file)
                
                st.session_state["df"] = df
                st.session_state["uploaded_file_name"] = data_file.name
                
                # --- New Requirement: List current capabilities ---
                info_string = f"Successfully loaded `{data_file.name}`. The dataset has **{df.shape[0]} rows** and **{df.shape[1]} columns**."
                
                capability_list = """
                **Current Capabilities:**
                
                1.  **Custom Plotting:** Use the **'📊 Create Custom Plot'** section below to interactively select axes and plot types.
                2.  **Chat Commands (Natural Language):**
                    * **`Show Statistics`** or **`Descriptive Statistics`**: Displays key statistics for numerical columns.
                    * **`Show Columns`** or **`List Columns`**: Lists all column names.
                    * **`Show Missing Values`** or **`Show Nulls`**: Summarizes missing counts and percentages.
                    * **`Show Head`** or **`First Rows`**: Displays the first 5 rows.
                """
                
                st.session_state["data_analysis_messages"] = [
                    {"role": "assistant", "content": info_string},
                    {"role": "assistant", "content": capability_list}
                ]
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.session_state.pop("df", None)
        
        if "df" in st.session_state:
            df = st.session_state["df"]
            st.write(f"**Dataset:** `{st.session_state.uploaded_file_name}`")
            
            # --- Custom Plotting UI using Expander ---
            with st.expander("📊 Create Custom Plot"):
                all_cols = df.columns.tolist()
                
                if not all_cols:
                    st.warning("No columns found in the dataset.")
                else:
                    # --- Input Widgets for Plotting ---
                    col_x, col_y, col_type = st.columns(3)
                    
                    # Ensure selection is safe, default to the first column
                    default_x_index = 0
                    default_y_index = min(1, len(all_cols) - 1) 

                    x_axis = col_x.selectbox("X-Axis", options=all_cols, index=default_x_index, key="plot_x")
                    y_axis = col_y.selectbox("Y-Axis", options=all_cols, index=default_y_index, key="plot_y")
                    
                    plot_options = ['Scatter', 'Bar', 'Line', 'Histogram', 'Box']
                    plot_type = col_type.selectbox(
                        "Plot Type", 
                        options=plot_options, 
                        key="plot_type"
                    )
                    
                    # Group By (Color) Selector
                    color_col = st.selectbox(
                        "Group By (Color)", 
                        options=['None'] + all_cols, 
                        index=0, 
                        key="plot_color"
                    )

                    # --- Plot Generation Button ---
                    if st.button("Generate Plot", key="generate_plot_btn"):
                        color = None if color_col == 'None' else color_col
                        
                        try:
                            # Plotly Express Plotting Logic
                            if plot_type == 'Scatter':
                                fig = px.scatter(df, x=x_axis, y=y_axis, color=color, title=f'Scatter Plot: {x_axis} vs {y_axis}')
                            elif plot_type == 'Line':
                                fig = px.line(df, x=x_axis, y=y_axis, color=color, title=f'Line Plot: {x_axis} vs {y_axis}')
                            elif plot_type == 'Bar':
                                fig = px.bar(df, x=x_axis, y=y_axis, color=color, title=f'Bar Plot: {x_axis} vs {y_axis}')
                            elif plot_type == 'Histogram':
                                # Histogram only needs X-axis
                                fig = px.histogram(df, x=x_axis, color=color, title=f'Histogram of {x_axis}')
                            elif plot_type == 'Box':
                                fig = px.box(df, x=x_axis, y=y_axis, color=color, title=f'Box Plot of {y_axis} by {x_axis}')

                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Could not generate plot. Please check if the data types of the selected columns are compatible with the plot type. Error: {e}")

            st.markdown("---")
            
            # --- Natural Language Chat Interface ---
            for msg in st.session_state.get("data_analysis_messages", []):
                with st.chat_message(msg["role"]):
                    if isinstance(msg["content"], pd.DataFrame):
                        st.dataframe(msg["content"])
                    else:
                        st.markdown(msg["content"])
            
            prompt = st.chat_input("Ask a question about your data...", key="data_input")
            if prompt:
                st.session_state["data_analysis_messages"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.spinner("🤖 Analyzing data..."):
                    response_content = None
                    response_message = "I'm sorry, I only understand the listed chat commands or can generate plots via the UI above."
                    prompt_lower = prompt.lower().strip()

                    # Logic to execute commands based on natural language
                    if "show statistics" in prompt_lower or "descriptive statistics" in prompt_lower:
                        try:
                            stats_df = df.describe().transpose()
                            stats_df.index.name = "Column"
                            response_content = stats_df
                            response_message = "Here are the descriptive statistics for the numerical columns in your dataset:"
                        except Exception as e:
                            response_message = f"I'm sorry, I couldn't generate statistics. Error: {e}"

                    elif "columns" in prompt_lower or "list columns" in prompt_lower:
                        response_message = f"The columns in your dataset are: `{'`, `'.join(df.columns)}`"
                        
                    elif "head" in prompt_lower or "first rows" in prompt_lower:
                        response_content = df.head()
                        response_message = "Here are the first 5 rows of your dataset:"
                        
                    elif "tail" in prompt_lower or "last rows" in prompt_lower:
                        response_content = df.tail()
                        response_message = "Here are the last 5 rows of your dataset:"

                    elif "missing values" in prompt_lower or "nulls" in prompt_lower:
                        null_counts = df.isnull().sum()
                        null_percentages = (null_counts / len(df)) * 100
                        missing_data = pd.DataFrame({'Missing Count': null_counts, 'Percentage': null_percentages}).T
                        response_content = missing_data
                        response_message = "Here is the summary of missing values in each column:"
                    
                    elif "hi" in prompt_lower or "hello" in prompt_lower:
                        response_message = f"Hello! I'm ready to help you analyze your `{st.session_state.uploaded_file_name}` dataset. Try one of the commands or use the plot UI."

                with st.chat_message("assistant"):
                    st.markdown(response_message)
                    if isinstance(response_content, pd.DataFrame):
                        st.dataframe(response_content)
                
                message_to_save = response_content if isinstance(response_content, pd.DataFrame) else response_message
                st.session_state["data_analysis_messages"].append(
                    {"role": "assistant", "content": message_to_save}
                )
    else:
        st.info("Upload a dataset above to get started.")
