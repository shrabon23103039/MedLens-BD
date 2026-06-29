from google import genai
from google.genai import types
import pdfplumber
import os
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ocr_image(image_bytes):
    """Extract text from handwritten/printed prescription image using Gemini Vision"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        This is a medical prescription or lab report image from Bangladesh.
        Extract ALL text from this image exactly as written.
        
        Pay special attention to:
        - Medicine/drug names (both Bengali and English)
        - Dosage instructions
        - Doctor's notes
        - Patient information
        - Lab values and results
        
        Return the raw extracted text only. Do not interpret or explain.
        If text is in Bengali, keep it in Bengali script.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[prompt, image]
        )
        return response.text.strip()

    except Exception as e:
        return f"OCR Error: {str(e)}"


def ocr_pdf(pdf_bytes):
    """Extract text from printed PDF prescription"""
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return "PDF appears to be scanned. Please upload as image."

        return text.strip()

    except Exception as e:
        return f"PDF Error: {str(e)}"


def extract_drug_names(raw_text):
    """Use Gemini to extract drug names from OCR text"""
    try:
        prompt = f"""
        From this prescription text extracted from a Bangladeshi prescription:
        
        {raw_text}
        
        Extract ONLY the medicine/drug names as a comma separated list.
        Include both brand names and generic names you can identify.
        Common Bangladeshi brands: Napa, Ace, Seclo, Moxacil, Glucophage,
        Amdocal, Atova, Fexo, Montek, Ciproflox, Ranitin etc.
        
        Return ONLY a comma separated list of drug names, nothing else.
        Example: Napa, Seclo, Glucophage, Amlodipine
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )

        raw = response.text.strip()
        drugs = [d.strip() for d in raw.split(",") if d.strip()]
        return drugs

    except Exception as e:
        print(f"Drug extraction error: {e}")
        return []


def process_prescription(file_bytes, file_type="image"):
    """
    Main function — takes file bytes, returns:
    - raw_text: extracted text
    - drug_names: list of identified drugs
    """
    if file_type == "pdf":
        raw_text = ocr_pdf(file_bytes)
    else:
        raw_text = ocr_image(file_bytes)

    drug_names = extract_drug_names(raw_text)

    return {
        "raw_text": raw_text,
        "drug_names": drug_names
    }


if __name__ == "__main__":
    sample_text = """
    Patient: Mohammad Ali
    Age: 45
    
    Rx:
    1. Napa 500mg - 1+1+1
    2. Seclo 20mg - 1+0+1
    3. Glucophage 500mg - 0+1+1
    4. Amdocal 5mg - 1+0+0
    """

    print("Testing drug extraction...")
    drugs = extract_drug_names(sample_text)
    print(f"✅ Extracted drugs: {drugs}")