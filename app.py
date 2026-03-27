import re
import zipfile
from io import BytesIO
from collections import defaultdict

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ashot Tools", page_icon="🛠️", layout="wide")
st.title("Ashot Tools")

# =========================
# Session state for Excel Splitter
# =========================
if "zip_data" not in st.session_state:
    st.session_state.zip_data = None
if "zip_name" not in st.session_state:
    st.session_state.zip_name = None
if "ready" not in st.session_state:
    st.session_state.ready = False

# =========================
# Domain Grouper config
# =========================
PROJECT_PATTERNS = {
    "1GO": ["1go"],
    "Drip": ["drip"],
    "Fresh": ["fresh"],
    "Galaktika 15": ["martin"],
    "Galaktika 16": ["beef"],
    "Galaktika 17": ["fugu"],
    "Gizbo": ["gizbo"],
    "Irwin": ["irwin"],
    "izzi": ["izzi"],
    "Jet": ["jet"],
    "Legzo": ["legzo"],
    "Lex": ["lex"],
    "Monro": ["monro"],
    "ROX": ["rox"],
    "SOL": ["sol"],
    "Starda": ["starda"],
    "Flagman": ["flagman"],
}

ALL_PATTERNS = []
for project, patterns in PROJECT_PATTERNS.items():
    for pattern in patterns:
        ALL_PATTERNS.append((project, pattern.lower()))

ALL_PATTERNS.sort(key=lambda x: len(x[1]), reverse=True)


def clean_domain(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    line = re.sub(r"^https?://", "", line, flags=re.IGNORECASE)
    line = line.strip("/")
    return line.lower()


def find_project(domain: str):
    for project, pattern in ALL_PATTERNS:
        if pattern in domain:
            return project
    return None


def group_domains(input_text: str) -> str:
    lines = input_text.splitlines()
    grouped = defaultdict(list)
    unknown = []
    seen = set()

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        cleaned = clean_domain(raw)
        project = find_project(cleaned)

        full_url = raw if raw.startswith(("http://", "https://")) else f"http://{cleaned}/"

        if full_url in seen:
            continue
        seen.add(full_url)

        if project:
            grouped[project].append(full_url)
        else:
            unknown.append(full_url)

    if not grouped and not unknown:
        return "No domains to process."

    result = []
    result.append("Hi, can you activate LiveTV for these domains as well? /ROX/\n")

    for project in sorted(grouped.keys()):
        result.append(f"{project}:")
        for domain in grouped[project]:
            result.append(domain)
        result.append("")

    if unknown:
        result.append("Unknown:")
        for domain in unknown:
            result.append(domain)
        result.append("")

    return "\n".join(result)


# =========================
# Tabs
# =========================
tab1, tab2 = st.tabs(["Excel Splitter", "ROX Domain Grouper"])

# =========================
# Tab 1: Excel Splitter
# =========================
with tab1:
    st.subheader("Excel Splitter")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"], key="excel_uploader")
    chunk_size = st.number_input("Rows per file", value=1000, min_value=1, step=1, key="chunk_size")

    if uploaded_file and st.button("Split", key="split_button"):
        with st.spinner("Processing your file..."):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
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
            mime="application/zip",
            key="download_zip"
        )

# =========================
# Tab 2: ROX Domain Grouper
# =========================
with tab2:
    st.subheader("ROX Domain Grouper")

    domain_input = st.text_area(
        "Paste domains (one per line)",
        height=300,
        placeholder="http://jetcasino527.com/\nhttp://gizbocasinovip37.com/",
        key="domain_input"
    )

    if st.button("Group Domains", key="group_domains_button"):
        st.session_state.grouped_result = group_domains(domain_input)

    if "grouped_result" in st.session_state:
        st.text_area(
            "Formatted output (ready to copy)",
            value=st.session_state.grouped_result,
            height=350,
            key="grouped_output"
        )
