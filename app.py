import streamlit as st
import dropbox
import pandas as pd
import re
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Dropbox to Shopify Image Link Generator",
    page_icon="favicon.png",  # Make sure this file is in the root directory of your project
    layout="wide"
)

# Inject custom fonts and branding
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Arimo:wght@400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
html, body, [class*='css'] {
    font-family: 'Arimo', sans-serif!important;
    background-color: #ffffff;
    color: #000000;
}
            .st-emotion-cache-16tyu1 {font-family: 'Arimo', sans-serif!important;}
            .st-emotion-cache-1xulwhk {padding: 10px;}
            .st-emotion-cache-4uzi61 {background: #fff;}
            .st-emotion-cache-jx6q2s {background: #F4F1EC;}
            .st-emotion-cache-qm7g72 {background-color: #000;}
            .st-emotion-cache-p7i6r9 {font-family: 'Arimo', sans-serif!important; text-transform: uppercase; font-size: 12px; color: #fff;}
            p {font-family: 'Arimo', sans-serif!important;}
            #em-dropbox-link-processor-em-bulk-convert {font-style: italic!important;}
            .st-bw {border: 1px solid #eee!important;}
           
            

h1, h2, h3 {
    font-family: 'Playfair Display', serif!important;
    color: #000000;
}
.stButton > button {
    background-color: #000000;
    color: #ffffff;
    border-radius: 6px;
    font-weight: bold;
    padding: 0.5em 1em;
    transition: all 0.3s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #333333;
            color: #fff;
}
.stDownloadButton > button {
    background-color: #000000;
    color: #ffffff;
    border-radius: 6px;
    font-weight: bold;
}
.stDataFrame, .stTextInput, .stTextArea, .stSelectbox, .stFileUploader {
    background-color: #ffffff;
    color: #000000;
}
div[data-testid='stMarkdownContainer'] > div {
    font-family: 'Arimo', sans-serif;
}
        

</style>
""", unsafe_allow_html=True)


st.title("📦 Dropbox Link Processor (Bulk Convert)")
st.write("Paste SKUs and Dropbox shared links from Excel into separate boxes. Generate shareable links for Matrixify export.")


# --- Logo Display in Sidebar ---
st.sidebar.markdown(
    """
    <div style='margin-bottom: 2rem;'>
        <img src="Logo-Black@2x.png" width="160">
    </div>
    """,
    unsafe_allow_html=True
)


# --- Dropbox API Setup ---
if 'access_token' not in st.session_state:
    with st.sidebar.form(key="token_form"):
        token_input = st.text_input("Enter your Dropbox API token", type="password")
        submit_token = st.form_submit_button("Submit Token")
        if submit_token and token_input:
            st.session_state['access_token'] = token_input

if 'access_token' not in st.session_state:
    st.warning("Please enter your Dropbox API token and click 'Submit Token'.")
    st.stop()

access_token = st.session_state['access_token']
dbx = dropbox.Dropbox(access_token)

# --- Start New Batch ---
if st.sidebar.button("🔁 Start New Batch"):
    for key in ['sku_input', 'link_input', 'converted_data', 'export_result', 'show_conversion_success', 'last_export_df', 'export_log', 'error_log', 'export_ready']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- Step 1: Input SKUs and Dropbox Links ---
st.subheader("1. Paste SKUs and Dropbox Shared Links")

if 'sku_input' not in st.session_state:
    st.session_state['sku_input'] = ""
if 'link_input' not in st.session_state:
    st.session_state['link_input'] = ""

sku_text = st.text_area("📋 Paste SKUs (one per line):", height=200, key="sku_input")
link_text = st.text_area("🔗 Paste Dropbox shared links (one per line, in the same order):", height=200, key="link_input")

sku_list = [line.strip() for line in sku_text.strip().splitlines() if line.strip()]
link_list = [line.strip() for line in link_text.strip().splitlines() if line.strip()]

if len(sku_list) != len(link_list):
    st.warning(f"⚠️ You have {len(sku_list)} SKUs and {len(link_list)} links. These must match.")
    st.stop()

# --- Convert to Folder Paths ---
if 'converted_data' not in st.session_state:
    st.session_state.converted_data = []
if 'show_conversion_success' not in st.session_state:
    st.session_state.show_conversion_success = False

if st.button("🔄 Convert to Folder Paths"):
    converted = []
    progress = st.progress(0)
    status = st.empty()
    for idx, link in enumerate(link_list):
        try:
            meta = dbx.sharing_get_shared_link_metadata(link)
            if isinstance(meta, dropbox.sharing.FolderLinkMetadata):
                path = meta.path_lower
                display = dbx.files_get_metadata(path).path_display
                converted.append(display)
        except Exception as e:
            st.error(f"Error processing link: {link} — {e}")
        progress.progress((idx + 1) / len(link_list))
        status.info(f"Processing link {idx + 1} of {len(link_list)}")
    st.session_state.converted_data = converted
    st.session_state.show_conversion_success = bool(converted)
    progress.empty()
    status.empty()

if st.session_state.get("show_conversion_success", False):
    st.success("✅ Dropbox links have been successfully converted to folder paths.")

# --- Step 2: Generate Image Links ---
st.subheader("2. Generate Image Links by SKU + Folder Path")

def natural_sort_key(file_name):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', file_name)]

def get_shared_link(file_path):
    try:
        links = dbx.sharing_list_shared_links(path=file_path).links
        for l in links:
            if isinstance(l, dropbox.sharing.FileLinkMetadata):
                return l.url
        return dbx.sharing_create_shared_link_with_settings(file_path).url
    except Exception:
        return None

def list_files_recursive(folder, error_log):
    links = []
    file_count = 0
    try:
        res = dbx.files_list_folder(folder)
        files = sorted(
            [e for e in res.entries if isinstance(e, dropbox.files.FileMetadata) and not e.name.lower().endswith(('.psd', '.png'))],
            key=lambda x: natural_sort_key(x.name)
        )
        for f in files:
            link = get_shared_link(f.path_lower)
            if link:
                links.append(link)
                file_count += 1
        for e in res.entries:
            if isinstance(e, dropbox.files.FolderMetadata):
                sub_links, sub_count = list_files_recursive(e.path_lower, error_log)
                links.extend(sub_links)
                file_count += sub_count
    except Exception as e:
        error_log.append(f"Failed to read folder '{folder}': {e}")
    return links, file_count

if st.button("📤 Generate and Export Image Links"):
    result = []
    export_log = []
    error_log = []
    folders = st.session_state.get("converted_data", [])
    progress = st.progress(0)
    status = st.empty()

    for idx, folder in enumerate(folders):
        sku = sku_list[idx]
        status.info(f"Processing {sku} ({idx+1}/{len(folders)})")
        image_links, count = list_files_recursive(folder, error_log)
        if image_links:
            result.append([sku, " ; ".join(image_links)])
            export_log.append(f"<div style='color: green;'>✅ <strong>{sku}</strong> — {count} images found.</div>")
        else:
            export_log.append(f"<div style='color: orange;'>⚠️ <strong>{sku}</strong> — No valid images found.</div>")
        progress.progress((idx + 1) / len(folders))

    progress.empty()
    status.empty()

    if export_log:
        st.session_state["export_log"] = export_log
    if result:
        df = pd.DataFrame(result, columns=["SKU", "All Image Links"])
        st.session_state["last_export_df"] = df
        st.session_state["export_ready"] = True

# Display log and download section after export (or persisted via session)
if st.session_state.get("export_ready", False):
    if "export_log" in st.session_state:
        html_summary = "".join(st.session_state["export_log"])
        st.markdown(
            f"<div style='max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;'>{html_summary}</div>",
            unsafe_allow_html=True
        )

    if "last_export_df" in st.session_state:
        df = st.session_state["last_export_df"]
        st.subheader("📊 Preview Table")
        st.dataframe(df)
        output = BytesIO()
        df.to_excel(output, index=False)
        st.success("✅ Excel generated with SKU + image links!")
        st.download_button("⬇ Download Excel File", data=output.getvalue(), file_name="dropbox_links_with_skus.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.session_state.get("error_log"):
        with st.expander("⚠️ View Errors"):
            for err in st.session_state["error_log"]:
                st.error(err)