# 📦 Dropbox to Shopify Image Link Generator

This internal tool allows you to generate direct image URLs from Dropbox folders and pair them with SKU codes — perfect for bulk uploading to Shopify using Matrixify.

---

## 🚀 Hosted App

Access the app here: [Your Streamlit App Link]  
> (Replace this with the Streamlit Cloud URL after deployment)

---

## 🧩 Features

- ✅ Convert Dropbox links into case-sensitive folder paths
- ✅ Generate public image links (excluding PSD/PNG files)
- ✅ Pair image links with SKU codes
- ✅ Preview results and download Excel output
- ✅ Built-in reset and progress indicators

---

## 🧑‍💻 How to Use

1. **Paste your Dropbox API token** in the sidebar and click **Submit Token**
2. **Paste SKUs** into the SKU field (one per line)
3. **Paste Dropbox shared folder links** (matching order)
4. Click **Convert to Folder Paths**
5. Click **Generate Image Links**
6. Preview the table and click **Download Excel File**
7. Click **Start New Batch** to begin again

---

## 🖥️ Local Development (Optional)

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
├── Logo-Black.svg       # Company logo for branding
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

For questions or feedback, contact the Digital Experience Manager.
