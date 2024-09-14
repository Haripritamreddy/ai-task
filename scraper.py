# scraper.py
import os
import bs4
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()

def scrape_and_add_documents():
    bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",), # Replace with your news source URLs
        bs_kwargs={"parse_only": bs4_strainer},
    )
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embedding_function = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv('GOOGLE_API_KEY'),model="models/text-embedding-004")

    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embedding_function,
        persist_directory="./chroma_langchain_2_db",
    )

    vector_store.add_documents(documents=docs)

if __name__ == "__main__":
    scrape_and_add_documents() 