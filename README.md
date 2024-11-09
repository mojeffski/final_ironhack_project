# final_ironhack_project

---
## Overview
This project integrates a scraper system to track national legislative procedures under EU notification processes. It retrieves metadata, draft laws, and comments from the EU Commission website using email alerts. The metadata is mapped to EU lobby register data, extracting network information from the membership section. All data is stored in an SQLite database, accessible via a LangChain agent, with documents processed using the Unstructured library and stored in a vector database.

## 1. Notification Scraper

The **Notification Scraper** is designed to scrape and process metadata and documents related to TRIS notifications (Technical Regulation Information System). 

### Scripts and Workflows
- **`1_TRIS_gmx_scraper.py`**:
  - This script connects to the TRIS alert system via an email account and retrieves recent notification alerts. The metadata is stored in an SQLite database (`scraper_data.db`).
  - **Setup Instructions**:
    - Register for the mailing list [here](https://technical-regulation-information-system.ec.europa.eu/de/the-20151535-and-you/being-informed/mailing-list/subscribe).
    - Create a `config.env` file with the necessary email credentials to automate alert retrieval.

- **`2_draft_law_scraper.ipynb`**:
  - This notebook downloads the metadata and related PDFs from the EU Commission's notification website.

---

## 2. Lobby Register Scraper

The **Lobby Register Scraper** focuses on extracting entity information from the EU Transparency Register. This provides insights into the organizations commenting on draft laws.

### Scripts and Workflows
- **`1_entity_EU_register_extraction.ipynb`**:
  - Extracts information about members and organizations from the EU Transparency Register, creating a network dataset.
  
- **`2_cleaning_post_extraction.ipynb`**:
  - Cleans and preprocesses the data extracted from the Transparency Register.

- **`3_evaluation.ipynb`**:
  - Evaluates the extracted information against hardcoded articles for quality assurance and consistency.

---

## 3. Multimodal RAG and Agents

This folder implements a Retrieval-Augmented Generation (RAG) system for answering questions and managing data relationships between legislative drafts and stakeholder comments.

### Scripts and Workflows
- **`3_question_answer.ipynb`**:
  - A notebook for querying the RAG system and generating answers based on input data.
  
- **`4_sql_agent.ipynb`**:
  - Manages SQL-based data querying and integration into the RAG pipeline.

- **Utilities**:
  - `preprocessing.py`: Prepares raw data for vectorization.
  - `txt_gen.py`: Generates text outputs for RAG models.
  - `vectors.py`: Handles vectorization and embedding tasks.

---
## Main Libraries and Dependencies

The project is built using **Python 3.12.7** and relies on the following main libraries:

- **[unstructured](https://github.com/Unstructured-IO/unstructured)**: For processing and extracting information from documents.
  - Additional dependencies: `tesseract` (for OCR) and `poppler-utils` (for PDF processing).
- **[LangChain](https://github.com/hwchase17/langchain)**: For building language model-powered applications.
- **[LangGraph](https://github.com/langchain/langgraph)**: For agent-based access to databases and vectorstores.
- **[Playwright](https://playwright.dev/)**: For headless browser automation in scraping tasks.

---

## Instructions for Running the Project

### 1. General
- The notebooks in this project are **independent** and can be run separately. 
- Each notebook serves a specific purpose, such as data extraction, cleaning, or evaluation.

---
#### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ironhack_final_project.git
cd ironhack_final_project
```

### 2. Setup and Installation
```bash
python3 -m venv venv
```
- activate the virtual environment

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Install Additional Dependencies
```bash
brew install tesseract
brew install poppler
```

