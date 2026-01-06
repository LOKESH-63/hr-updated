from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import (
    AZURE_CHAT_DEPLOYMENT,
    AZURE_EMBEDDING_DEPLOYMENT,
    OPENAI_API_VERSION
)

def build_rag_pipeline(pdf_path: str):

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    # Embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=AZURE_EMBEDDING_DEPLOYMENT,
        api_version=OPENAI_API_VERSION
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # LLM
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_CHAT_DEPLOYMENT,
        api_version=OPENAI_API_VERSION,
        temperature=0.0
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an HR Policy Assistant.

Answer ONLY using the HR policy content below.
If the answer is not found, say:

"I checked the HR policy document, but this information is not mentioned. Please contact HR."

HR Policy Content:
{context}

Question:
{question}

Answer:
"""
    )

    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
