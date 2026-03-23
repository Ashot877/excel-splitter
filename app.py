import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO

st.title("Excel Splitter by Ashot")

if "zip_data" not in st.session_state:
    st.session_state.zip_data = None
if "zip_name" not in st.session_state:
    st.session_state.zip_name = None
if "ready" not in st.session_state:
    st.session_state.ready = False

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
chunk_size = st.number_input("Rows per file", value=1000, min_value=1, step=1)

if uploaded_file and st.button("Split"):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    elif file_name.endswith(".xls"):
        df = pd.read_excel(uploaded_file, engine="xlrd")
    else:
        st.error("Unsupported file format")
        st.stop()

    base_name = uploaded_file.name.rsplit(".", 1)[0]
    zip_filename = f"{base_name}_split.zip"

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            part_filename = f"{base_name}_{i // chunk_size + 1}.xlsx"

            excel_buffer = BytesIO()
            chunk.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            z.writestr(part_filename, excel_buffer.read())

    zip_buffer.seek(0)
    st.session_state.zip_data = zip_buffer.read()
    st.session_state.zip_name = zip_filename
    st.session_state.ready = True

if st.session_state.ready:
    st.success("Done! Your file is ready.")
    st.download_button(
        label="Download ZIP",
        data=st.session_state.zip_data,
        file_name=st.session_state.zip_name,
        mime="application/zip"
    )
