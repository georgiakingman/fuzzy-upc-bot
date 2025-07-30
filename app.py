import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("GK Fuzzy Product Code Matcher")
st.write("""
Upload two CSV files:

- A **reference** CSV that contains the correct `ITEM_NAME` and `UPC`
- An **input** CSV with messy `Description`s to match

The app will match your descriptions to the closest item name and return the UPC.
""")
reference_file = st.file_uploader("📘 Upload reference CSV (with ITEM_NAME and UPC)", type="csv")
input_file = st.file_uploader("📗 Upload input CSV (with Description)", type="csv")
if reference_file and input_file:
    reference_df = pd.read_csv(reference_file)
    input_df = pd.read_csv(input_file)
    reference_name_col = 'ITEM_NAME'
    reference_code_col = 'UPC'
    input_name_col = 'Description'
    reference_names = reference_df[reference_name_col].tolist()
    def match_item_name(item_name):
        if pd.isna(item_name):
            return pd.Series([None, None])
        result = process.extractOne(item_name, reference_names, scorer=fuzz.token_sort_ratio)
        if result is None:
            return pd.Series([None, None])
        matched_name, score = result[0], result[1]
        matched_row = reference_df[reference_df[reference_name_col] == matched_name]
        if matched_row.empty:
            return pd.Series([None, score])
        matched_code = matched_row.iloc[0][reference_code_col]
        return pd.Series([matched_code, score])
    input_df[['Matched UPC', 'Match Score']] = input_df[input_name_col].apply(match_item_name)
    st.success("✅ Matching complete!")
    st.dataframe(input_df)
    csv_output = input_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Matched CSV", csv_output, "matched_output.csv", "text/csv")
