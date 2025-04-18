import os

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        Ты — дружелюбный, заботливый и внимательный ассистент поддержки вымышленной кофейни «Дрова и Зёрна». Твоя задача — отвечать на вопросы клиентов из предоставленной информаци. Отвечай на вопросы сухо и кратко на столько, на сколько возможно без потери смысла. В каждом сообщении будь вежливым и желай пользователю хорошего настроения. Если не можешь найти подходящей информации в контексте ответь: \"не знаю\"
        Контекст:
        {context}

        Вопрос: {question}
        Ответ:
    """,
)


# Устанавливаем токен Hugging Face

# 1. Загружаем документы из файла
loader = TextLoader("my_docs.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
documents = splitter.split_documents(documents)
print("parts len: ", len(documents))
# 2. Создаем эмбеддинги с помощью модели sentence-transformers
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# embeddings = OllamaEmbeddings(model="nomic-embed-text")
try:
    print("try to load")
    vectorstore = FAISS.load_local(
        "./db", embeddings, allow_dangerous_deserialization=True
    )
    print("loaded")
except Exception as e:
    print("save\n", e)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local("./db")


# appropriate = vectorstore.similarity_search("как по шагам работает RAG?", 4)
# [print(page.page_content) for page in appropriate]

llm = OllamaLLM(
    model="llama3.2",
    temperature=0.1,
)


qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": prompt_template},
)

while True:
    query = input("Введите ваш вопрос (или 'выход' для завершения): ")

    appropriate = vectorstore.similarity_search(query)
    print("\n", "\n".join([page.page_content for page in appropriate]), "\n")

    if query.lower() in ["q", "выход"]:
        print("Завершение программы.")
        break
    answer = qa.invoke({"query": query})
    print("Ответ:", answer["result"])
