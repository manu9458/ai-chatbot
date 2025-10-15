# 🪐 Aurora Genie: Advanced GenAI & Data Analysis Platform

A modular, multi-section application built with **Streamlit** and **Pandas** that leverages the **Google Gemini LLM** for both conversational AI and powerful data insights.

## Core Chat & Document Features

The application provides foundational generative AI tools with robust features:

* **General Q/A Chat**: Provides real-time, streaming responses for general inquiries using Google Search grounding.

* **Document Q/A**: Users can upload **PDF or DOCX files** and ask questions grounded entirely in the document content.

* **Persistent History**: Maintains separate, persistent chat history for both Q/A and Document sections using Streamlit Session State.

---

## 📈 AI-Powered Data Analysis Studio (New Features)

The new Data Analysis section transforms unstructured data analysis using AI and dedicated tools.

| Feature Area | Functionality Added | Technical Implementation |
| :--- | :--- | :--- |
| **Data Interaction** | **LLM-Powered Data Queries**: Translates natural language questions (e.g., "highest sale," "top 10 cities") into executable data analysis, replacing rule-based commands. | Uses **Gemini LLM** with the entire DataFrame as context for complex, dynamic queries. |
| **Data Exploration** | **Automated Data Profiling**: Generates a comprehensive **yData-profiling** report for instant data quality assessment. | Uses `ydata-profiling` to output a full HTML report, provided via a one-click download. |
| **Data Cleaning** | **Data Cleaning Assistant**: Provides a UI for one-click operations: dropping duplicates and filling missing values (Mean/Median/Static value). | Changes are applied in place to the cached DataFrame, with a dedicated button to **download the cleaned dataset.** |
| **Visualization** | **Dashboard Mode**: Offers interactive, multi-plot dashboards (Histogram, Scatter Plot) with user-selectable columns and integrated filters (Date Range, Category). | Uses **Plotly Express** for interactivity and Streamlit UI components for custom filtering. |
| **Advanced Analysis** | **Time Series Forecasting**: Forecasts future values based on historical data using a **Simple Moving Average** model, provided a datetime column is present. | Includes logic to automatically parse date columns for immediate forecasting. |
| **Usability** | **Caching and Export**: Data loading is **cached** (`@st.cache_data`) for performance. Cleaned data, plots, and the EDA report can be exported. | Improves performance by minimizing disk read operations upon app rerun. |

---

## Project Structure & Setup

This project follows a modular structure for maintainability:

| File/Folder | Purpose |
| :--- | :--- |
| `app.py` | Main Streamlit application and navigation. |
| `data_analysis.py` | Core module for the data analysis section and chat interface. |
| `eda_utils.py` | **New module** containing modular functions for Data Profiling, Outlier Detection, and Cleaning. |
| `gemini_client.py` | Initializes the Gemini API client and handles response streaming. |
| `config.py` | Environment variable and model configuration. |
| `doc_utils.py` | Functions for extracting text from PDF/DOCX files. |
| `logger.py` | Centralized logging setup (outputs to `logs/app.log`). |
| `.streamlit/` | **New folder** containing `config.toml` for UI/UX custom theme settings. |
| `requirements.txt` | Lists all necessary dependencies (`pandas`, `plotly`, `ydata-profiling`, `openpyxl`, `tabulate`, `setuptools`). |