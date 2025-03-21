import os
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Qdrant

class EmbeddingsManager:
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en",
        device: str = "cpu",
        encode_kwargs: dict = {"normalize_embeddings": True},
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "vector_db",
    ):
        self.model_name = model_name
        self.device = device
        self.encode_kwargs = encode_kwargs
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name

        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": self.device},
            encode_kwargs=self.encode_kwargs,
        )

    def create_embeddings(self, folder_path: str):
        """
        Processes all PDFs in a folder, creates embeddings, and stores them in Qdrant.

        Args:
            folder_path (str): The path to the folder containing PDF documents.

        Returns:
            str: Success message upon completion.
        """
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The folder {folder_path} does not exist.")

        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        if not pdf_files:
            raise ValueError("No PDF files found in the specified folder.")

        all_splits = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)

            loader = UnstructuredPDFLoader(pdf_path)
            docs = loader.load()
            if not docs:
                raise ValueError(f"No documents were loaded from the PDF {pdf_file}.")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=250
            )
            splits = text_splitter.split_documents(docs)
            if not splits:
                raise ValueError(f"No text chunks were created from the document {pdf_file}.")
            
            all_splits.extend(splits)

        try:
            qdrant = Qdrant.from_documents(
                all_splits,
                self.embeddings,
                url=self.qdrant_url,
                prefer_grpc=False,
                collection_name=self.collection_name,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Qdrant: {e}")

        return "✅ Vector DB Successfully Created and Stored in Qdrant!"
