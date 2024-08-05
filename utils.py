
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

import os
from dotenv import load_dotenv,find_dotenv
from langchain_openai import OpenAI
_ = load_dotenv(find_dotenv())
OpenAI(api_key = os.environ.get('OPENAI_API_KEY'))\


class DocumentHandler:
    def __init__(self,path_to_document):
        self.loader = PyPDFDirectoryLoader(path_to_document)
        self.splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','],
                                                       chunk_size=600,
                                                       chunk_overlap=0)

    def load_split_document(self):
        try:
            docs = self.loader.load_and_split(self.splitter)
            return docs
        except Exception as e:
            print(f"Error loading and splitting documents: {e}")
            return None

class VectorDBHandler:
    def __init__(self,vector_db_path):
        self.vector_db_path = vector_db_path
        self.vector_db = None

    def initialize_db(self, docs):
        try:
            embeddings = OpenAIEmbeddings()
            self.vector_db = Chroma.from_documents(docs, embeddings,persist_directory=self.vector_db_path)
        except Exception as e:
            print(f"Error initializing vector database: {e}")

    def search_context(self, query):
        try:
            self.vector_db = Chroma(persist_directory=self.vector_db_path,embedding_function=OpenAIEmbeddings())
            # return [context for context,score in self.vector_db.similarity_search_with_relevance_scores(query) if score >0.65]
            return self.vector_db.max_marginal_relevance_search(query,k=2,fetch_k=4)
        except Exception as e:
            print(f"Error searching vector database: {e}")
            return None

class PromptHandler:
    def __init__(self, template):
        self.template = template
        self.prompt_template = PromptTemplate(input_variables=['context', 'question', 'chat_history'], template=self.template)

    def get_prompt_template(self):
        try: 
            return self.prompt_template
        except Exception as e:
            print(f"Error creating prompt template: {e}")
            return None

def initialize_memory():
    try:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key='question')
        return memory
    except Exception as e:
        print(f"Error initializing memory: {e}")
        return None
