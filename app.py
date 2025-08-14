import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "food_data.db"

# Database connection
def get_connection():
    return sqlite3.connect(DB_PATH)

# Load table data
def load_data(table_name):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# CRUD operations
def add_listing(food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    conn = get_connection()
    conn.execute(
        "INSERT INTO listings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
    )
    conn.commit()
    conn.close()

def update_listing(food_id, quantity):
    conn = get_connection()
    conn.execute("UPDATE listings SET Quantity = ? WHERE Food_ID = ?", (quantity, food_id))
    conn.commit()
    conn.close()

def delete_listing(food_id):
    conn = get_connection()
    conn.execute("DELETE FROM listings WHERE Food_ID = ?", (food_id,))
    conn.commit()
    conn.close()

# ---------------- Streamlit UI ----------------

st.title("🍲 Local Food Wastage Management System")

menu = ["Home", "Filter Listings", "CRUD Operations", "Reports & Queries"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Database Overview")
    for table in ["providers", "receivers", "listings", "claims"]:
        st.write(f"### {table.capitalize()} Table")
        st.dataframe(load_data(table))

elif choice == "Filter Listings":
    st.subheader("🔍 Filter Food Donations")
    listings = load_data("listings")
    
    city_filter = st.selectbox("Select Location", ["All"] + sorted(listings["Location"].unique().tolist()))
    provider_filter = st.selectbox("Select Provider Type", ["All"] + sorted(listings["Provider_Type"].unique().tolist()))
    food_filter = st.selectbox("Select Food Type", ["All"] + sorted(listings["Food_Type"].unique().tolist()))
    
    filtered = listings.copy()
    if city_filter != "All":
        filtered = filtered[filtered["Location"] == city_filter]
    if provider_filter != "All":
        filtered = filtered[filtered["Provider_Type"] == provider_filter]
    if food_filter != "All":
        filtered = filtered[filtered["Food_Type"] == food_filter]
    
    st.dataframe(filtered)

elif choice == "CRUD Operations":
    st.subheader("➕ Add New Listing")
    with st.form("add_form"):
        food_id = st.number_input("Food ID", step=1)
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", step=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", step=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        submitted = st.form_submit_button("Add Listing")
        if submitted:
            add_listing(food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
            st.success("Listing added successfully!")

    st.subheader("✏️ Update Listing Quantity")
    with st.form("update_form"):
        food_id_update = st.number_input("Food ID to Update", step=1)
        new_quantity = st.number_input("New Quantity", step=1)
        submitted_update = st.form_submit_button("Update")
        if submitted_update:
            update_listing(food_id_update, new_quantity)
            st.success("Listing updated successfully!")

    st.subheader("🗑 Delete Listing")
    with st.form("delete_form"):
        food_id_delete = st.number_input("Food ID to Delete", step=1)
        submitted_delete = st.form_submit_button("Delete")
        if submitted_delete:
            delete_listing(food_id_delete)
            st.success("Listing deleted successfully!")

elif choice == "Reports & Queries":
    st.subheader("📊 Analysis & Queries")
    conn = get_connection()

    # Example Query - Providers by City
    q1 = pd.read_sql("""
        SELECT City, COUNT(*) as Provider_Count 
        FROM providers 
        GROUP BY City
    """, conn)
    st.write("### Providers by City")
    st.dataframe(q1)

    fig, ax = plt.subplots()
    ax.bar(q1["City"], q1["Provider_Count"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    conn.close()
