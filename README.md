# Data Cleaner App

A web app to upload, clean, and preview datasets. Supports CSV, Excel, TSV, JSON, and SQLite files.

## Features
- Upload datasets
- Remove duplicate rows or columns
- Remove rows with missing values
- Preview dataset, duplicates, and missing values
- Download cleaned data as CSV

## How to Run Locally

Clone the repository:
git clone https://github.com/jamshidfarook/Data-Cleaner-App.git
cd Data-Cleaner-App

Install requirements:
pip install -r requirements.txt

Run the app:
python app.py

Open in browser:
http://127.0.0.1:5000/

## Notes
- Make sure the uploads/ folder exists in the project root for file uploads.
- Works with Python 3.10+.
