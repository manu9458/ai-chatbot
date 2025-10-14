import streamlit as st
import pandas as pd
import plotly.express as px
from eda_utils import generate_eda_report, detect_outliers, data_cleaning_assistant
from gemini_client import get_gemini_client, stream_gemini_response

# A cached function to load the data, improving performance
@st.cache_data
def load_data(uploaded_file):
    """
    Reads the uploaded file into a pandas DataFrame.
    """
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == 'xlsx':
        df = pd.read_excel(uploaded_file)
    elif file_extension == 'txt':
        # Assuming a comma-separated format for text files
        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            # Fallback for plain text files
            df = pd.DataFrame({'content': [uploaded_file.read().decode()]})
            
    return df

def display_data_analysis():
    """
    Display the AI-Powered Data Analysis section for CSV/Excel file upload and exploration.
    This function contains the core logic for EDA using natural language and plotting UI.
    """
    st.subheader("AI-Powered Data Analysis")
    st.info("Upload a CSV, Excel, or Text file and start exploring your data with chat commands or custom plots.")

    # File uploader for data
    data_file = st.file_uploader(
        "Upload a CSV, XLSX, or TXT file",
        type=["csv", "xlsx", "txt"],
        key="data_uploader"
    )

    client = get_gemini_client()

    if data_file:
        # Check if a new file is uploaded or if the session state DataFrame is missing
        if "df" not in st.session_state or st.session_state.uploaded_file_name != data_file.name:
            try:
                # Read the file into a DataFrame using the new cached function
                df = load_data(data_file)
                st.session_state["df"] = df
                st.session_state["uploaded_file_name"] = data_file.name
                
                # --- Updated: List current capabilities ---
                info_string = f"Successfully loaded `{data_file.name}`. The dataset has **{df.shape[0]} rows** and **{df.shape[1]} columns**."
                
                capability_list = """
                **Current Capabilities:**
                
                1.  **Dashboard Mode:** See a quick overview of your key data metrics and plots.
                2.  **Geospatial Analysis:** If your data contains lat/lon coordinates, a map will be generated.
                3.  **Data Queries (AI Assistant):** Ask me anything in natural language about your dataset.
                4.  **Data Cleaning Assistant:** Easily remove duplicates and fill missing values.
                5.  **Outlier Detection:** Visualize and find outliers in numerical columns.
                6.  **Custom Plotting:** Use the **'投 Create Custom Plot'** section below to interactively select axes and plot types.
                7.  **Correlation Heatmap:** Generate a heatmap showing the correlation between numerical columns.
                8.  **Automatic Data Profiling:** Generates a full EDA report.
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
            
            # --- New Dashboard Mode with user-selected columns ---
            with st.expander("📈 Dashboard Mode"):
                st.write("A quick overview of key data visualizations.")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                # User selection for dashboard plots
                if numeric_cols:
                    st.markdown("##### Select Columns for Dashboard Plots")
                    col_dash1, col_dash2 = st.columns(2)
                    
                    hist_col = col_dash1.selectbox("Select a column for Histogram:", options=numeric_cols, key="dash_hist_col")
                    scatter_x = col_dash2.selectbox("Select X-Axis for Scatter Plot:", options=numeric_cols, key="dash_scatter_x")
                    scatter_y = col_dash2.selectbox("Select Y-Axis for Scatter Plot:", options=numeric_cols, key="dash_scatter_y")

                    # Display the plots
                    if hist_col and scatter_x and scatter_y:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### Distribution Plot")
                            fig_hist = px.histogram(df, x=hist_col)
                            st.plotly_chart(fig_hist, use_container_width=True)
                        
                        with col2:
                            st.markdown("##### Scatter Plot")
                            fig_scatter = px.scatter(df, x=scatter_x, y=scatter_y)
                            st.plotly_chart(fig_scatter, use_container_width=True)

                # Check for location data for a map
                location_cols = ['latitude', 'longitude']
                if all(col in df.columns for col in location_cols):
                    st.markdown("##### Geospatial Analysis")
                    st.info("Geospatial data detected! Displaying data points on a map.")
                    fig_map = px.scatter_mapbox(
                        df, 
                        lat="latitude", 
                        lon="longitude", 
                        zoom=3, 
                        mapbox_style="carto-positron"
                    )
                    st.plotly_chart(fig_map, use_container_width=True)

            # Call the new data cleaning assistant function
            with st.expander("🧹 Data Cleaning Assistant"):
                data_cleaning_assistant()

            # Call the existing outlier detection function
            with st.expander("🚨 Outlier Detection"):
                detect_outliers(df)

            # Call the existing function for data profiling
            with st.expander("📊 Automatic Data Profiling"):
                generate_eda_report(df, st.session_state.uploaded_file_name)

            # --- Correlation Heatmap Expander ---
            with st.expander("📊 Correlation Heatmap"):
                st.write("Show the correlation between numerical features.")
                if st.button("Generate Heatmap"):
                    numeric_df = df.select_dtypes(include=['number'])
                    if not numeric_df.empty:
                        corr_matrix = numeric_df.corr()
                        fig = px.imshow(
                            corr_matrix, 
                            text_auto=True, 
                            title="Correlation Heatmap",
                            labels=dict(color="Correlation")
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No numerical columns found to create a heatmap.")
            
            # --- Custom Plotting UI using Expander ---
            with st.expander("Create Custom Plot"):
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
                
                with st.spinner("✨ Aurora is analyzing your data..."):
                    response = None
                    prompt_lower = prompt.lower().strip()
                    
                    # Dictionary mapping common queries to pandas operations
                    query_mapping = {
                        "highest sale": lambda df: df[df.select_dtypes(include='number').columns].max().to_markdown(),
                        "total sum of sale": lambda df: df[df.select_dtypes(include='number').columns].sum().to_markdown(),
                        "total return": lambda df: df[df.columns[df.columns.str.contains('return', case=False)]].sum().to_markdown(),
                        "highest profit": lambda df: df[df.columns[df.columns.str.contains('profit', case=False)]].max().to_markdown(),
                        "top 10 city with highest sales": lambda df: df.groupby('City')['Sales'].sum().nlargest(10).to_markdown() if 'City' in df.columns and 'Sales' in df.columns else "Required columns not found.",
                        "top 10 customer buying frequently": lambda df: df['Customer Name'].value_counts().nlargest(10).to_markdown() if 'Customer Name' in df.columns else "Required column 'Customer Name' not found.",
                        "payment mode": lambda df: df['Payment Mode'].unique().to_markdown() if 'Payment Mode' in df.columns else "Required column 'Payment Mode' not found."
                    }

                    # Check for a match in the query mapping
                    for query, func in query_mapping.items():
                        if query in prompt_lower:
                            try:
                                result = func(df)
                                # Prepare a simple, direct prompt for the AI with the calculated result
                                full_prompt = f"Given the following calculation result:\n{result}\n\nPlease summarize this information for the user in a helpful, conversational manner. Do not mention that you've performed a calculation or use the term 'pandas'."
                                response = stream_gemini_response(client, full_prompt, st.session_state.get("data_analysis_messages", []))
                                break
                            except Exception as e:
                                response = f"An error occurred while trying to fulfill your request: {e}. Please check your dataset columns."
                                break
                    
                    # If no specific query was matched, fall back to the general LLM approach
                    if not response:
                        data_context = df.to_markdown()
                        full_prompt = (
                            "You are an AI data analyst. Your task is to answer questions about a provided dataset. "
                            "When answering, you must use the context provided below. "
                            "If the question requires a calculation or specific value, "
                            "you MUST perform the calculation and provide the result based on the provided data context. "
                            "If the user asks for information not present in the provided context, "
                            "you must explicitly state that the information cannot be found in the dataset and refrain from generating a fabricated answer."
                            "Do not make up any information.\n\n"
                            f"Dataset Context:\n{data_context}\n"
                            f"User Question: {prompt}"
                        )
                        response = stream_gemini_response(
                            client,
                            full_prompt,
                            st.session_state.get("data_analysis_messages", []),
                        )
                    
                if response:
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state["data_analysis_messages"].append(
                        {"role": "assistant", "content": response}
                    )
    else:
        st.info("Upload a dataset above to get started.")