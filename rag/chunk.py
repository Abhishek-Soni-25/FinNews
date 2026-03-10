import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(file_path, chunk_size=800, chunk_overlap=100):
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []

    current_part = None
    current_item = None
    current_section = None
    current_subsection = None

    buffer = []

    def flush_buffer():
        """Convert buffered text into chunks with metadata"""
        nonlocal buffer

        text = "\n".join(buffer).strip()
        if not text:
            buffer = []
            return

        split_chunks = splitter.split_text(text)

        for c in split_chunks:
            chunks.append({
                "text": c,
                "metadata": {
                    "part": current_part or "",
                    "item": current_item or "",
                    "section": current_section or "",
                    "subsection": current_subsection or "",
                    "source": file_path
                }
            })

        buffer = []

    for line in lines:

        line = line.rstrip()

        # Detect PART
        if re.match(r"#\s*PART\s+[IVX]+", line, re.IGNORECASE):
            flush_buffer()
            current_part = line.strip()
            continue

        # Detect ITEM
        if re.match(r"#+\s*Item\s+\d+[A-Z]?", line, re.IGNORECASE):
            flush_buffer()
            current_item = line.strip()
            current_section = None
            current_subsection = None
            continue

        # Detect SECTION
        if re.match(r"###\s+", line):
            flush_buffer()
            current_section = line.replace("###", "").strip()
            current_subsection = None
            continue

        # Detect SUBSECTION
        if re.match(r"####\s+", line):
            flush_buffer()
            current_subsection = line.replace("####", "").strip()
            continue

        buffer.append(line)

    flush_buffer()

    return chunks