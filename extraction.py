import fitz
doc = fitz.open("data/building_rag_ebook.pdf")
text = ""

for page in doc:
    text += page.get_text()

print(text[:500])