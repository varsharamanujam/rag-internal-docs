import re
import fitz  # PyMuPDF


def clean_fast(text: str) -> str:
    # Very safe cleanup (no expensive regex patterns)
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences_simple(text: str) -> list[str]:
    # Simple, fast sentence split
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def build_sentence_chunks_from_pdf(
    pdf_path: str,
    chunk_size_chars: int = 1200,
    overlap_sentences: int = 2,
    max_pages: int = 5,          # safety: only first N pages for now
    max_total_chars: int = 200_000,  # safety: cap total processed characters
    per_page_char_cap: int = 50_000,  # safety: cap individual page extraction
) -> list[str]:
    doc = fitz.open(pdf_path)

    chunks = []
    current_sentences = []
    current_len = 0
    processed_chars = 0
    prev_overlap = []

    for page_idx, page in enumerate(doc):
        if page_idx >= max_pages:
            break

        try:
            # "text" is usually lighter than default; avoids layout-heavy extraction
            page_text = page.get_text("text") or ""
        except Exception as e:
            print(f"Skipping page {page_idx+1} due to extraction error: {e}")
            continue

        # light clean
        page_text = clean_fast(page_text)
        if not page_text:
            continue

        # cap per-page to avoid one page blowing memory
        if per_page_char_cap is not None:
            page_text = page_text[:per_page_char_cap]

        # cap total chars to avoid crashes
        remaining = max_total_chars - processed_chars
        if remaining <= 0:
            break
        page_text = page_text[:remaining]
        processed_chars += len(page_text)
        print(f"page={page_idx+1} chars_processed={processed_chars}")

        sentences = split_into = split_sentences_simple(page_text)

        # prepend overlap from previous page (if any)
        if prev_overlap:
            sentences = prev_overlap + sentences
            prev_overlap = []

        i = 0
        while i < len(sentences):
            s = sentences[i]
            add_len = len(s) + (1 if current_sentences else 0)

            # if single sentence is huge, cut it
            if not current_sentences and len(s) > chunk_size_chars:
                chunks.append(s[:chunk_size_chars])
                i += 1
                continue

            if current_len + add_len <= chunk_size_chars:
                current_sentences.append(s)
                current_len += add_len
                i += 1
            else:
                # finalize chunk
                chunk_text = " ".join(current_sentences).strip()
                if chunk_text:
                    chunks.append(chunk_text)

                # overlap
                if overlap_sentences > 0:
                    # keep the last few sentences as starting point for next chunk
                    current_sentences = current_sentences[-overlap_sentences:]
                    current_len = len(" ".join(current_sentences))
                else:
                    current_sentences = []
                    current_len = 0

        # store overlap across pages (take at most available sentences)
        if overlap_sentences > 0:
            prev_overlap = sentences[-overlap_sentences:] if len(sentences) >= overlap_sentences else sentences[:]

    # flush final
    final_text = " ".join(current_sentences).strip()
    if final_text:
        chunks.append(final_text)

    return chunks


if __name__ == "__main__":
    pdf_path = "data/building_rag_ebook.pdf"
    chunks = build_sentence_chunks_from_pdf(
        pdf_path,
        chunk_size_chars=1200,
        overlap_sentences=2,
        max_pages=15,            # ✅ safe default
        max_total_chars=300_000, # ✅ safe default
        per_page_char_cap=50_000
    )

    print("Chunks:", len(chunks))
    if chunks:
        print("First chunk length:", len(chunks[0]))
        print("Last chunk length:", len(chunks[-1]))
        print("\n--- First chunk preview (first 500 chars) ---\n")
        print(chunks[0][:500])