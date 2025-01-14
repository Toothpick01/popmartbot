from docx import Document
import os

def extract_sections_excluding_bold_titles(doc_path, output_folder):
    """
    Extracts sections from a Word document where titles are bold, and saves each section into a separate text file
    excluding the bold titles.
    :param doc_path: Path to the Word document.
    :param output_folder: Folder to save the text files.
    """
    document = Document(doc_path)
    sections = []
    current_section = []
    
    for paragraph in document.paragraphs:
        # Check if the paragraph has bold text
        if any(run.bold for run in paragraph.runs):
            # If there's an existing section, save it
            if current_section:
                sections.append("\n".join(current_section).strip())
                current_section = []
            # Skip adding the bold paragraph to the current section
            continue
        current_section.append(paragraph.text)
    
    # Append the last section
    if current_section:
        sections.append("\n".join(current_section).strip())

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save each section to a separate text file
    for idx, section in enumerate(sections, start=1):
        file_path = os.path.join(output_folder, f"section_{idx}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(section)
        print(f"Saved: {file_path}")

def main():
    # Path to the Word document
    doc_path = "F_A.docx"  # Replace with the path to your Word document
    # Output folder for section text files
    output_folder = "sections"

    print("Extracting sections...")
    extract_sections_excluding_bold_titles(doc_path, output_folder)
    print("Extraction completed! Check the 'sections' folder.")

if __name__ == "__main__":
    main()
