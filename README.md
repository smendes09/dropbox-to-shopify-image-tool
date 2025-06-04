# 📦 Dropbox to Shopify Image Link Generator

This internal tool allows you to generate direct image URLs from Dropbox folders and pair them with SKU codes — perfect for bulk uploading to Shopify using Matrixify.

---

## 🚀 Hosted App

Access the app here: [https://dropbox-to-shopify-image-tool-iyzfew6f7bkfky7wv9qjww.streamlit.app/](https://dropbox-to-shopify-image-tool-iyzfew6f7bkfky7wv9qjww.streamlit.app/)
> (Replace this with the Streamlit Cloud URL after deployment)

---

## 🧩 Features

- ✅ Paste tab-separated SKU + Dropbox link pairs from Excel
- ✅ Convert Dropbox shared links into case-sensitive folder paths
- ✅ Automatically generate public image links (excluding PSD/PNG/JPG files)
- ✅ Export clean Excel file ready for Matrixify
- ✅ Built-in success indicators, error logging, and batch reset

---

## 🧑‍💻 How to Use

1. **Paste your Dropbox API token** in the sidebar and click **Submit Token**
2. **Copy both SKU and Dropbox shared links from Excel** (two adjacent columns)
3. **Paste into the unified input field** (each line = SKU<TAB>Dropbox Link)
4. Click **Process & Export All** to begin
5. View the conversion summary and preview table
6. Click **Download Excel File** to export the data
7. Click **Start New Batch** to clear everything and begin again

> 💡 *Tip: No need to manually add tabs — just copy both columns directly from Excel or Google Sheets.*

---

## 💻 Local Development (Optional)

Clone the repo and run the app locally:

```bash
git clone https://github.com/YOUR-ORG/dropbox-to-shopify-image-tool.git
cd dropbox-to-shopify-image-tool
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Folder Contents

```
dropbox-to-shopify-image-tool/
├── app.py               # Streamlit app script
├── favicon.png          # Favicon used in browser tab
├── logo-black.png       # Company logo for branding
├── requirements.txt     # Python dependencies
└── README.md            # Instructions for usage
```

---

## 🔐 Dropbox API Token

To generate your token:
- Visit [https://www.dropbox.com/developers/apps](https://www.dropbox.com/developers/apps)
- Create an app with `files.metadata.read` and `files.content.read`
- Click **Generate Token** and copy it into the app

---

## 💬 Support

For questions or feedback, contact the Digital Experience Manager or reach out via the #automation-support Slack channel.
