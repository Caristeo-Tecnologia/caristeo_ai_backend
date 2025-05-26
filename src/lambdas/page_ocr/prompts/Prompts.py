class Prompts:
    PAGE_OCR_PROMPT = """
    You are an expert in epigraphy and archaic languages. Do OCR on this image and transcribe PERFECTLY ALL the words on the page. Reason in length and verbosely.
    Transcribe ALL text visible in this image with perfect accuracy.    
    
    IMPORTANT INSTRUCTIONS:

    - Return ONLY the transcribed text formatted as Markdown
    - Remove artificial line breaks within paragraphs to create continuous flowing text
    - Format the text using Markdown conventions:
      - Use ## for page titles and main headings
      - Use ### for section titles and subheadings
      - Format article numbers (like "ART. 2°") in **bold** (using standard Markdown bold)
      - Use proper paragraph spacing with blank lines between paragraphs
      - Use Markdown lists for enumerated items
      - Use > for indented or quoted text sections
    - Use standard Markdown bold formatting with two asterisks (\*\*) for emphasized text
    - If a word is split between lines, write it as a single word (e.g., "Palavra" instead of "Pala-vra")
    - Do not describe what you're doing or what the image contains
    - Do not use any HTML formatting, stick to pure Markdown syntax
    """.strip()
