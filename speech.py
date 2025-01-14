import os
import time
from gtts import gTTS

def convert_sections_to_speech(input_folder, output_folder, language, start_section=1, delay=2):
    """
    Converts text files to speech audio files starting from a specific section.
    
    Args:
        input_folder (str): Path to the folder containing text files.
        output_folder (str): Path to the folder to save audio files.
        language (str): Language for TTS.
        start_section (int): Section number to start from.
        delay (int): Delay in seconds between TTS requests.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get a sorted list of text files
    text_files = sorted(f for f in os.listdir(input_folder) if f.endswith('.txt'))
    
    # Ensure proper alignment with section numbers
    for text_file in text_files:
        section_number = int(os.path.splitext(text_file)[0].split('_')[-1])  # Extract section number
        if section_number < start_section:
            continue  # Skip until reaching the specified starting section
        
        input_file = os.path.join(input_folder, text_file)
        output_file = os.path.join(output_folder, f"{os.path.splitext(text_file)[0]}.mp3")
        
        if os.path.exists(output_file):
            print(f"Skipping {text_file} as the audio file already exists.")
            continue  # Skip if the audio file already exists

        print(f"Processing section {section_number}: {text_file}")
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Generate speech and save as an audio file
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_file)
            print(f"Saved {output_file}")
        except Exception as e:
            print(f"Error processing {text_file}: {e}")
        
        # Add a delay to prevent overwhelming the TTS service
        time.sleep(delay)

def main():
    input_folder = "sections"  # Folder with text files
    output_folder = "audios"  # Folder to save audio files
    language = "de"  # German language code
    start_section = 1  # Change to the section you want to start from
    delay = 3  # Delay in seconds between requests

    print("Starting speech conversion...")
    convert_sections_to_speech(input_folder, output_folder, language, start_section=start_section, delay=delay)
    print("Speech conversion completed!")

if __name__ == "__main__":
    main()
