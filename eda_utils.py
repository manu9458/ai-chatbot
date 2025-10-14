import streamlit as st
import pandas as pd
import plotly.express as px
from ydata_profiling import ProfileReport
import os

def generate_eda_report(df, filename):
    """
    Generates an automated data profiling report using ydata-profiling.
    The report is saved to an HTML file and a download button is provided.
    
    Args:
        df (pd.DataFrame): The DataFrame to profile.
        filename (str): The name of the original uploaded file.
    """
    st.subheader("📊 Automated Data Profiling")
    st.info("Generates a comprehensive EDA report in HTML format.")

    if st.button("Generate & Download EDA Report"):
        with st.spinner("Generating EDA report... This may take a moment for large datasets."):
            try:
                # Create a ProfileReport object
                profile = ProfileReport(
                    df, 
                    title=f"EDA Report for {filename}", 
                    html={"style": {"full_width": True}},
                    sort=None
                )
                
                # Save the report to a temporary HTML file
                report_path = f"report_{os.path.basename(filename).split('.')[0]}.html"
                profile.to_file(report_path)
                
                # Provide a download button for the generated file
                with open(report_path, "rb") as file:
                    st.download_button(
                        label="Download EDA Report",
                        data=file,
                        file_name=report_path,
                        mime="text/html"
                    )
                st.success("Report generated! Click the button to download.")

                # Clean up the temporary file
                os.remove(report_path)
            except Exception as e:
                st.error(f"Error generating report. Please ensure the 'ydata-profiling' library is installed. Error: {e}")


def detect_outliers(df):
    """
    Displays a UI to detect and visualize outliers in a numerical column.
    """
    st.subheader("异常 Outlier Detection")
    st.info("Visualize potential outliers in numerical columns using a box plot and statistical analysis.")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numerical columns found in the dataset for outlier detection.")
        return

    selected_col = st.selectbox(
        "Select a numerical column to analyze for outliers:",
        options=numeric_cols,
        key="outlier_col"
    )

    if st.button("Analyze Outliers"):
        # Plot a box plot for visual outlier detection
        st.write(f"**Box Plot of {selected_col}**")
        fig = px.box(df, y=selected_col)
        st.plotly_chart(fig, use_container_width=True)

        # Statistical analysis using IQR method
        Q1 = df[selected_col].quantile(0.25)
        Q3 = df[selected_col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
        
        st.write(f"**Potential Outliers (IQR Method):**")
        st.info(f"An outlier is defined as a value outside the range: "
                f"[{lower_bound:.2f}, {upper_bound:.2f}]")
        
        if not outliers.empty:
            st.warning(f"Found **{len(outliers)}** potential outliers in column `{selected_col}`.")
            st.dataframe(outliers)
        else:
            st.success("No significant outliers detected based on the IQR method.")


def export_dataframe(df):
    """
    Exports a DataFrame to a CSV file and provides a download button.
    """
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned Data as CSV",
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv',
    )


def data_cleaning_assistant():
    """
    Provides a UI for common data cleaning operations like dropping duplicates and filling missing values.
    """
    st.subheader("🧹 Data Cleaning Assistant")
    st.info("Apply common data cleaning operations directly to your dataset.")
    
    # Ensure there is a DataFrame to work with
    if "df" not in st.session_state or st.session_state["df"].empty:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state["df"]
    
    # 1. Drop Duplicates Section
    st.markdown("### Remove Duplicate Rows")
    st.write("Click the button to remove duplicate rows from the dataset.")
    if st.button("Drop Duplicates"):
        original_rows = len(df)
        df.drop_duplicates(inplace=True, ignore_index=True)
        st.session_state["df"] = df
        removed_rows = original_rows - len(df)
        st.success(f"Successfully removed **{removed_rows}** duplicate rows.")
        st.info(f"The dataset now has **{len(df)}** rows.")
    st.markdown("---")

    # 2. Fill Missing Values Section
    st.markdown("### Fill Missing Values")
    st.write("Fill missing values (NaN) in a selected column with a specified value.")
    
    missing_cols = df.columns[df.isnull().any()].tolist()
    
    if not missing_cols:
        st.success("No columns with missing values were found.")
    else:
        col_to_fill = st.selectbox(
            "Select a column with missing values:", 
            options=missing_cols
        )
        
        fill_option = st.selectbox(
            "Choose a method to fill missing values:",
            options=["Fill with a static value", "Fill with the mean", "Fill with the median"]
        )
        
        if fill_option == "Fill with a static value":
            fill_value = st.text_input(
                f"Enter the value to fill in column '{col_to_fill}':",
                key="static_fill_value"
            )
            if st.button("Apply Static Fill"):
                if fill_value:
                    df[col_to_fill] = df[col_to_fill].fillna(fill_value)
                    st.session_state["df"] = df
                    st.success(f"Missing values in `{col_to_fill}` filled with `{fill_value}`.")
                else:
                    st.warning("Please enter a value to fill.")
        
        elif fill_option == "Fill with the mean":
            if st.button("Apply Mean Fill"):
                if pd.api.types.is_numeric_dtype(df[col_to_fill]):
                    mean_val = df[col_to_fill].mean()
                    df[col_to_fill].fillna(mean_val, inplace=True)
                    st.session_state["df"] = df
                    st.success(f"Missing values in `{col_to_fill}` filled with the mean (**{mean_val:.2f}**).")
                else:
                    st.error("Mean fill is only applicable to numerical columns.")

        elif fill_option == "Fill with the median":
            if st.button("Apply Median Fill"):
                if pd.api.types.is_numeric_dtype(df[col_to_fill]):
                    median_val = df[col_to_fill].median()
                    df[col_to_fill].fillna(median_val, inplace=True)
                    st.session_state["df"] = df
                    st.success(f"Missing values in `{col_to_fill}` filled with the median (**{median_val:.2f}**).")
                else:
                    st.error("Median fill is only applicable to numerical columns.")

    st.markdown("---")
    st.write("### Cleaned Data Preview")
    st.dataframe(st.session_state["df"].head())

    # --- New: Export button inside the Data Cleaning Assistant section ---
    st.markdown("---")
    export_dataframe(st.session_state["df"])