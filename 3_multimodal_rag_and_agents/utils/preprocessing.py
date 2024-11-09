import os
import uuid
from unstructured.partition.auto import partition

def extract_elements_with_metadata(full_path, metadata=None):
    """
    Extract elements from a file based on its extension and attach metadata.
    path: File path, used to save images if extracted.
    fname: File name with extension.
    metadata: Dictionary of metadata to attach to each element.
    """
    
    print(f"Processing: {full_path}")

    # Partition and extract document elements
    elements = partition(
        filename=full_path,
        include_page_breaks=True,
        extract_images_in_pdf=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        #combine_text_under_n_chars=2000,
        image_output_dir_path=full_path,
    )

    # Attach metadata to each element if provided
    if metadata is None:
        metadata = {}
        print(f'THERE HAVE BEEN {len(elements)} EXTRACTED')
    for element in elements:
        #print(str(type(element)))
        # Convert element to a dictionary if necessary and add metadata
        
        element.metadata = {**metadata}  # Directly attach metadata to each element
        #print('ELEMENT:   ',element)

    return elements

# Categorize elements by type and retain metadata
def categorize_elements(raw_elements):
    """
    Categorize extracted elements into tables and texts, retaining metadata.
    raw_elements: List of unstructured.documents.elements.
    """
    tables = []
    texts = []
    for element in raw_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            
            tables.append({"content": str(element), "metadata": element.metadata})
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            texts.append({"content": str(element), "metadata": element.metadata})
    return texts, tables
