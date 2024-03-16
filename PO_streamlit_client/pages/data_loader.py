import pandas as pd
import streamlit as st
import datetime
from mongo_connection import upsert_records, delete_all, insert_data, find_with_po, records_dataframe


existing_record_df= pd.DataFrame()
# Function to update record status
def update_record_status(df, index, status_column, new_status):
    # Set the selected status column to new_status (True or False)
    df.at[index, status_column] = new_status
    
    # Set all other status columns to False
    other_status_columns = [col for col in df.columns if col.startswith("Material Status") and col != status_column]
    for col in other_status_columns:
        df.at[index, col] = False

po_no=st.text_input("Insert the po_number", key="po_number_input")

po_no_found=find_with_po(po_no)
st.write("Po found",po_no_found)
po_data=records_dataframe(po_no_found)
st.write("Po found dataframe",po_data)

if not po_no_found:
    uploaded_file = st.file_uploader('Upload a file')

    if uploaded_file is not None:
        df=pd.read_excel(uploaded_file)

        df["Material Status Yet to Order"]=[True for i in range(len(df))]
        df["Material Status in Transport"]=[False for i in range(len(df))]
        df["Material Status Delivered"]=[False for i in range(len(df))]
        df["Transport details"] = ""
        df["Vendor details"]=""
        df['PO_data_date']=datetime.datetime.now().strftime("%d/%m/%Y")

        df.insert(0, 'PO_data_date', df.pop('PO_data_date'))
        
        #Function to edit the data in streamlit webapp
        po_df=st.data_editor(df,num_rows="dynamic")


     
        if po_df is not None:
            if st.button("Insert records"):
                try:
                    insert_data(po_df)
                    st.write("Insertion successful")
                except Exception as e:
                    st.write('Insertion failed', e)
    if st.button("delete records"):
        try:
            delete_all()
            st.write("deleting all records")
        except Exception as e:
            st.write('Deleting operation fail', e)
else:
    # If PO number is found, provide options to update record status
    if not po_data.empty:
        st.write("PO Data:")
        st.write(po_data)

        # Allow user to select a record from the dataframe to update its status
        selected_index = st.selectbox("Select a record index to update status:", po_data.index)

        # Display current status of the selected record
        current_status = st.radio("Current Status:", ['Yet to Order', 'In Transport', 'Delivered'])

        # Provide options to update status
        new_status = st.radio("Update Status To:", ['Yet to Order', 'In Transport', 'Delivered'])

        if st.button("Update Status"):
            status_column = None
            if new_status == 'Yet to Order':
                status_column = 'Material Status Yet to Order'
            elif new_status == 'In Transport':
                status_column = 'Material Status in Transport'
            elif new_status == 'Delivered':
                status_column = 'Material Status Delivered'

            if status_column:
                update_record_status(po_data, selected_index, status_column, True)
                st.write("Status updated successfully.")
                
                # Retrieve existing record from the database and update it
                existing_record_cursor = find_with_po(po_no)
                existing_record_df = pd.DataFrame((existing_record_cursor))
                st.write('existing',existing_record_df)
                #update_record_status(existing_record_df, selected_index, status_column, True)
                
                # Insert updated record into the database
                #try
                upsert_records(existing_record_df)
                st.write("Updated record inserted successfully.")
                #except Exception as e:
                #st.write('Insertion failed', e)
            else:
                st.write("Invalid status update.")
                
        # Display the updated DataFrame after status update
        st.write("Updated PO Data:")
        st.write(po_data)
    else:
        st.write("No records found for the provided PO number.")
