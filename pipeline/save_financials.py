import os
import asyncio
from dotenv import load_dotenv
from sec_api import PdfGeneratorApi
from llama_cloud import AsyncLlamaCloud

load_dotenv()

EDGAR_API_KEY = os.getenv("EDGAR_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY") 

pdf_generator = PdfGeneratorApi(EDGAR_API_KEY)

SAVE_DIR = "data"
MD_DIR = os.path.join(SAVE_DIR, "markdown")
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

companies = {
    "AAPL": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
    "MSFT": "https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm",
    "GOOG": "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm",
    "TSLA": "https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm",
    "NVDA": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm",
}

async def parse_pdf_to_markdown(client: AsyncLlamaCloud, pdf_path: str, md_path: str):
    # 1) Upload PDF
    file_obj = await client.files.create(file=pdf_path, purpose="parse")
    print("File uploaded successfully")

    # 2) Parse -> markdown
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",          
        version="latest",
        expand=["markdown"],   
    )
    print("Parsed document received")

    # 3) Concatenate pages’ markdown
    pages = result.markdown.pages
    md_content = "\n\n".join(page.markdown for page in pages)

    # 4) Save to .md
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

async def main():
    client = AsyncLlamaCloud(api_key=LLAMA_CLOUD_API_KEY)

    for ticker, url in companies.items():
        # Download PDF from SEC (via sec-api)
        pdf_filename = f"{ticker.lower()}_10k.pdf"
        pdf_path = os.path.join(SAVE_DIR, pdf_filename)

        if not os.path.exists(pdf_path):
            pdf_content = pdf_generator.get_pdf(url)
            with open(pdf_path, "wb") as f:
                f.write(pdf_content)
            print(f"Downloaded: {pdf_filename}")
        else:
            print(f"Already exists: {pdf_filename}")

        # Parse to markdown using LlamaCloud
        md_filename = f"{ticker.lower()}_10k.md"
        md_path = os.path.join(MD_DIR, md_filename)

        print(f"Parsing {pdf_filename} -> {md_filename} ...")
        await parse_pdf_to_markdown(client, pdf_path, md_path)
        print(f"Saved markdown: {md_path}")

    print(f"PDFs in: {os.path.abspath(SAVE_DIR)}")
    print(f"MDs in:  {os.path.abspath(MD_DIR)}")

if __name__ == "__main__":
    asyncio.run(main())
