from utils import db_interaction
def split_text_if_needed(text, max_chars=1000):
    
    # Split the text only if it exceeds max_chars
    if len(text) <= max_chars:
        return [text]  # Return the text as a single-element list

    # Otherwise, split by line breaks into chunks that respect max_chars
    words = text.splitlines()
    chunks, current_chunk = [], ""
    
    for line in words:
        if len(current_chunk) + len(line) + 1 <= max_chars:
            current_chunk += "\n" + line if current_chunk else line
        else:
            chunks.append(current_chunk)
            current_chunk = line  # Start a new chunk
    if current_chunk:
        chunks.append(current_chunk)  # Add the last chunk

    return chunks


def process_data(row, runnable, insert_func):
    global counter
    check_intervals = 50
    id = row['id']
    member_of_text = row['member_of']

    # Split text if needed
    text_chunks = split_text_if_needed(member_of_text, max_chars=1000)

    all_extracted_data = []
    for chunk in text_chunks:
        data = runnable.invoke({"text": chunk})
        print(f"Chunk Extracted data for ID {id}: {data.organisations}")
        all_extracted_data.extend(data.organisations)
    
    # Insert all extracted data at once
    insert_func(id, all_extracted_data)
    session.flush()  # Ensures all pending changes are written
    
    # Confirm insertion
    if session.query(OrganisationModel).filter_by(custom_id=id).first():
        print(f"Confirmed entry for {id} exists post-insertion.")
    
    counter += 1
    if counter % check_intervals == 0:
        print(f"Processed another {check_intervals} entries. Total count: {counter}")
        
        
# Step 1: Exclude all rows from the DataFrame that have already been processed
def exclude_processed_rows(df,session):
    existing_ids = session.query(db_interaction.OrganisationModel.custom_id).distinct().all()
    existing_ids = [x[0] for x in existing_ids]  # Flatten the list of tuples to a list of IDs
    return df[~df['id'].isin(existing_ids)]  # Filter out rows where id is already in the database


def exclude_processed_rows_without_results(df,session):
    processed_ids = session.query(db_interaction.ProcessingLog.custom_id).distinct().all()
    processed_ids = [x[0] for x in processed_ids]  # Flatten the list of tuples to a list of IDs
    return df[~df['id'].isin(processed_ids)]  # Exclude rows with already processed IDs