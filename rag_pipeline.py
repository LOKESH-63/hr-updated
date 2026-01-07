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

def build_rag_pipeline(pdf_path: str, temperature: float = 0.2):

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=AZURE_EMBEDDING_DEPLOYMENT,
        api_version=OPENAI_API_VERSION
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = AzureChatOpenAI(
        azure_deployment=AZURE_CHAT_DEPLOYMENT,
        api_version=OPENAI_API_VERSION,
        temperature=temperature
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an HR Policy Assistant.

Answer ONLY from the HR policy content.
If not found, say politely:
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

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
