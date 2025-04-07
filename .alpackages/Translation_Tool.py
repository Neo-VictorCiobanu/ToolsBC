import os
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
import deepl

# Register the XML namespaces
ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

# Initialize DeepL with your API key
# Replace 'YOUR_DEEPL_API_KEY' with your actual DeepL API key
translator = deepl.Translator("944c5ead-7384-4fbd-a373-29bd2b1a09ea:fx")

def process_xlf_file(file_path):
    """Process a single XLF file, translate untranslated elements and save the result."""
    print(f"Processing file: {file_path.name}")
    
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Get target language from file element
    file_element = root.find('.//{urn:oasis:names:tc:xliff:document:1.2}file')
    target_language = file_element.get('target-language')
    
    if not target_language:
        print(f"No target language specified in {file_path.name}")
        return 0
    
    print(f"Target language: {target_language}")
    
    # Get base language code for DeepL (e.g., 'FI' from 'fi-FI')
    base_lang = target_language.split('-')[0].upper()
    
    # Find all trans-unit elements
    trans_units = root.findall('.//{urn:oasis:names:tc:xliff:document:1.2}trans-unit')
    print(f"Found {len(trans_units)} trans-units to process")
    
    translated_count = 0
    
    # Process each trans-unit
    for trans_unit in trans_units:
        source_element = trans_unit.find('.//{urn:oasis:names:tc:xliff:document:1.2}source')
        target_element = trans_unit.find('.//{urn:oasis:names:tc:xliff:document:1.2}target')
        
        # Check if target needs translation - now checking for both conditions
        if (target_element is not None and 
            (target_element.text == '[NAB: NOT TRANSLATED]' or 
             (target_element.text is not None and '[NAB: SUGGESTION]' in target_element.text)) and 
            source_element is not None):
            
            source_text = source_element.text
            
            try:
                # Translate from English to target language
                translation = translator.translate_text(
                    source_text,
                    source_lang="EN",
                    target_lang=base_lang
                )
                
                # Update the target with the translation
                target_element.text = translation.text
                translated_count += 1
                
                # Update the relevant note
                notes = trans_unit.findall('.//{urn:oasis:names:tc:xliff:document:1.2}note')
                for note in notes:
                    if note.get('from') == 'NAB AL Tool Refresh Xlf' and note.text in ['New translation.', 'Suggestion.']:
                        note.text = target_element.text
            except Exception as e:
                print(f"Error translating '{source_text}': {str(e)}")
    
    print(f"Translated {translated_count} out of {len(trans_units)} trans-units")
    
    # Create Results directory if it doesn't exist
    results_dir = file_path.parent / 'Result'
    results_dir.mkdir(exist_ok=True)
    
    # Write the updated XML to the Results directory
    output_path = results_dir / file_path.name
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    
    print(f"Translated file saved to: {output_path}")
    return translated_count

def main():
    """Find and process all XLF files in the current directory."""
    try:
        # Get current directory
        current_dir = Path.cwd()
        
        # Find all .xlf files in the current directory
        xlf_files = list(current_dir.glob('*.xlf'))
        
        if not xlf_files:
            print('No .xlf files found in the current directory')
            return
        
        print(f"Found {len(xlf_files)} .xlf files to translate")
        
        # Process Cibes Aesy Customizations.fi-FI.xlf first if it exists
        target_first = current_dir / 'Cibes Aesy Customizations.fi-FI.xlf'
        if target_first in xlf_files:
            xlf_files.remove(target_first)
            xlf_files.insert(0, target_first)
        
        # Process each .xlf file
        total_translated = 0
        for file_path in xlf_files:
            count = process_xlf_file(file_path)
            total_translated += count
        
        print(f"Translation complete! Total translated items: {total_translated}")
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()