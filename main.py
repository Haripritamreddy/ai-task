# import
import os
import bs4
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
documents = loader.load()

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# create the open-source embedding function
embedding_function = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv('GOOGLE_API_KEY'),model="models/text-embedding-004")

# load it into Chroma
db = Chroma.from_documents(docs, embedding_function)

# query it
query = "certifications done?"
docs = db.similarity_search(query)

# print results
print(docs[0].page_content)