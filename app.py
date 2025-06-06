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
            .st-emotion-cache-1fmfajh {background-color: #fff;}
            .st-emotion-cache-17estbc {background-color: #fff;}
            .stButton > button {color: #fff!important;}
            #1-paste-skus-and-dropbox-shared-links {font-family: 'Arimo', sans-serif!important;}
            .st-emotion-cache-10c9vv9 {text-transform: uppercase; font-size: 12px !important;}
           
            

h1, h2, h3 {
    font-family: 'Playfair Display', serif!important;
    color: #000000;
}
h3 {
    font-family: 'Arimo', sans-serif!important;
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
.stDataFrame, .stTextArea, .stSelectbox, .stFileUploader {
    background-color: #ffffff;
    color: #000000;
}
div[data-testid='stMarkdownContainer'] > div {
    font-family: 'Arimo', sans-serif;
}
        

</style>
""", unsafe_allow_html=True)


st.title("Dropbox Link Processor (Bulk Convert)")
st.write("Paste SKUs and Dropbox shared links from Excel into separate boxes. Generate shareable links for Matrixify export.")


# --- Logo Display in Sidebar ---


st.sidebar.image("logo-black.png", width=160)
st.sidebar.markdown("<div style='font-size: 12px; color: #666; margin-top: -10px;'><em>Version</em> 1.0</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")


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
    for key in [
        'sku_input', 'link_input', 'combined_input', 'converted_data', 'export_result',
        'show_conversion_success', 'last_export_df', 'export_log',
        'error_log', 'export_ready', 'process_time_display',
        'export_done', 'run_export_triggered'
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# --- Step 1: Input SKUs and Dropbox Links ---
st.markdown("---")
st.subheader("1. Paste SKUs and Dropbox Shared Links")

if 'sku_input' not in st.session_state:
    st.session_state['sku_input'] = ""
if 'link_input' not in st.session_state:
    st.session_state['link_input'] = ""

st.markdown("**📋 Paste SKU and Dropbox Link (tab-separated, one pair per line):**")
st.markdown("*Tip: Copy both columns (SKU + Dropbox Link) directly from Excel or Google Sheets and paste them below. No need to manually add tabs!*")


if 'combined_input' not in st.session_state:
    st.session_state['combined_input'] = ""

st.text_area(label="", height=300, key="combined_input")
combined_input = st.session_state["combined_input"]

sku_list, link_list = [], []
for i, line in enumerate(combined_input.strip().splitlines()):
    parts = line.strip().split("\t")
    if len(parts) != 2:
        st.warning(f"⚠️ Line {i+1} is not properly formatted: '{line}'")
        continue
    sku, link = parts
    sku_list.append(sku.strip())
    link_list.append(link.strip())



if len(sku_list) != len(link_list):
    st.warning(f"⚠️ You have {len(sku_list)} SKUs and {len(link_list)} links. These must match.")

# Validate each Dropbox link
invalid_links = []
for link in link_list:
    if not re.match(r"^https://www\.dropbox\.com/scl/fo/", link):
        invalid_links.append(link)

if invalid_links:
    st.error("❌ The following links are invalid shared Dropbox folder links:")
    for bad_link in invalid_links:
        st.code(bad_link)
    st.stop()
    st.stop()

# --- Convert to Folder Paths ---
st.markdown("---")
if 'converted_data' not in st.session_state:
    st.session_state.converted_data = []
if 'show_conversion_success' not in st.session_state:
    st.session_state.show_conversion_success = False





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
            [e for e in res.entries if isinstance(e, dropbox.files.FileMetadata) and not e.name.lower().endswith(('.psd', '.png', '.jpg'))],
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




# Create placeholders and controls
cols = st.columns([2, 3])
with cols[0]:
    if st.button("Process & Export All"):
        st.session_state['run_export_triggered'] = True
        st.session_state['export_done'] = False
        st.session_state['processing_in_progress'] = True  # ✅ NEW LINE
    
        # --- Combined Folder Path Conversion ---
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
            status.info(f"Converting link {idx + 1} of {len(link_list)}")
        st.session_state.converted_data = converted
        st.session_state.show_conversion_success = bool(converted)
        
        
        progress.empty()
        status.empty()
    
        if not converted:
            st.error("No valid folder paths could be extracted. Please check your links.")
            st.stop()
with cols[1]:
    timer_placeholder = st.empty()

# Only run export process if triggered and not already completed

# Display conversion success message if applicable
if st.session_state.get("show_conversion_success"):
    st.success('✅ Dropbox links have been successfully converted to folder paths.')

if st.session_state.get('run_export_triggered') and not st.session_state.get('export_done'):
    st.session_state['run_export_triggered'] = False  # Reset trigger
    st.session_state['export_done'] = True  # Mark as completed
    st.session_state['processing_in_progress'] = False  # ✅ NEW LINE

    result = []
    total_images = 0
    export_log = []
    error_log = []
    folders = st.session_state.get("converted_data", [])
    progress = st.progress(0)
    status = st.empty()

    import time
    start_time = time.time()

    for idx, folder in enumerate(folders):
        sku = sku_list[idx]

        elapsed = time.time() - start_time
        avg_time = elapsed / (idx + 1)
        est_remaining = avg_time * (len(folders) - idx - 1)

        elapsed_fmt = time.strftime('%M:%S', time.gmtime(elapsed))
        remaining_fmt = time.strftime('%M:%S', time.gmtime(est_remaining))

        status.info(f"⏱️ Processing {sku} ({idx+1}/{len(folders)})\nElapsed: {elapsed_fmt} — Est. remaining: {remaining_fmt}")

        image_links, count = list_files_recursive(folder, error_log)
        if image_links:
            total_images += len(image_links)
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
        df = pd.DataFrame(result, columns=["Variant SKU", "Image Src"])
        # Replace www.dropbox.com with dl.dropboxusercontent.com in all links
        df["Image Src"] = df["Image Src"].apply(
            lambda x: " ; ".join([
                link.replace("https://www.dropbox.com", "https://dl.dropboxusercontent.com")
                for link in x.split(" ; ")
            ])
        )
        df["Image Command"] = "REPLACE"
        st.session_state["last_export_df"] = df
        st.session_state["export_ready"] = True
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)

    st.session_state["process_time_display"] = (
        f"✅ Process completed in {minutes} minutes {seconds} seconds — "
        f"{total_images} images generated from {len(folders)} SKUs."
    )

    


# Display log and download section after export (or persisted via session)


if st.session_state.get("export_ready", False) and not st.session_state.get("processing_in_progress", False):
    
    # Checkbox to filter only error SKUs
    show_errors_only = st.checkbox("Show only SKUs with errors", value=False)

    if "export_log" in st.session_state:
        logs = st.session_state["export_log"]
        if show_errors_only:
            logs = [log for log in logs if "orange" in log or "Failed" in log]
        html_summary = "".join(logs)
        st.markdown(
            f"<div style='max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;'>{html_summary}</div>",
            unsafe_allow_html=True
        )

    # ✅ Move process time message display here:
    if st.session_state.get("process_time_display"):
        st.markdown(
            f"""<div style="background-color: #f3e8ff; border-left: 4px solid #a855f7; padding: 8px 12px; font-size: 16px; font-weight: bold; color: #1a1a1a; border-radius: 4px; display: inline-block; margin-top: 30px;">
            {st.session_state["process_time_display"]}
            </div>""",
            unsafe_allow_html=True
        )


    if "last_export_df" in st.session_state:
        df = st.session_state["last_export_df"]
        st.markdown("---")
        st.markdown("#### 📊 Preview Table")
        st.dataframe(df)
        output = BytesIO()
        df.to_excel(output, index=False)
        st.success("✅ Excel generated with SKU + image links!")
        st.markdown("---")
        st.subheader("3. Download Excel")
        st.download_button("⬇ Download Excel File", data=output.getvalue(), file_name="dropbox_links_with_skus.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.session_state.get("error_log"):
        with st.expander("⚠️ View Errors"):
            for err in st.session_state["error_log"]:
                st.error(err)
# --- Version Display in Sidebar ---