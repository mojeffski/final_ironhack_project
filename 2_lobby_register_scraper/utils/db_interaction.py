from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

# Initialize the base class for declarative class definitions
Base = declarative_base()

# Define the Organisation model
class OrganisationModel(Base):
    __tablename__ = 'organisations'

    # Autoincrementing ID
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # The custom ID (e.g., from external data source)
    custom_id = Column(String, nullable=False)  # Assuming your ID is string-based
    
    # Organisation details
    name = Column(String, nullable=True)
    url = Column(String, nullable=True)
    abbreviation = Column(String, nullable=True)

# Set up the engine and session
engine = create_engine('sqlite:///../db/organisations.db')
Base.metadata.create_all(engine)  # Create the table if it does not exist

Session = sessionmaker(bind=engine)
session = Session()

# Set up logging
logging.basicConfig(filename='insert_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')



def insert_organisations(id, organisations):
    try:
        if not organisations:
            # Log cases with no information found
            no_info_entry = ProcessingLog(custom_id=id, status='no_info', message="No relevant information found.")
            session.add(no_info_entry)
            session.commit()
            logging.info(f"No relevant information for {id}. Logged as no_info.")
            print(f"No relevant information for {id}. Logged as no_info.")
            return  # Exit since there's nothing to insert into the main table

        for org in organisations:
            new_org = OrganisationModel(
                custom_id=id,
                name=org.org_name,
                url=org.org_url,
                abbreviation=org.org_abbrev
            )
            session.add(new_org)
        
        session.commit()
        logging.info(f"Data for {id} successfully committed to the database.")
        print(f"Data for {id} successfully committed to the database.")
    
    except Exception as e:
        # Log the error in the ProcessingLog table and rollback the session
        session.rollback()
        error_entry = ProcessingLog(custom_id=id, status='error', message=str(e))
        session.add(error_entry)
        session.commit()
        logging.error(f"Failed to insert data for {id}. Error: {str(e)}")
        print(f"Failed to insert data for {id}. Error: {str(e)}")


# Define a table for logging irrelevant entries or errors
class ProcessingLog(Base):
    __tablename__ = 'processing_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    custom_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # e.g., 'no_info' or 'error'
    message = Column(String, nullable=True)  # Message or reason for status

# Create both tables
Base.metadata.create_all(engine)