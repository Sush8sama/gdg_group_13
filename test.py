from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai

PROJECT_ID = "texttospeeach-476609"
display_name = "test_corpus"
paths = ["gs://dutchbucket/500_750_processed_be_nl_2025_09_23"]

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location="europe-west3")

print("Creating RAG corpus...")
# Create RagCorpus with embedding model
embedding_model_config = rag.RagEmbeddingModelConfig(
    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        publisher_model="publishers/google/models/text-embedding-005"
    )
)

rag_corpus = rag.create_corpus(
    display_name=display_name,
    backend_config=rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    ),
)
print(f"Corpus created: {rag_corpus.name}")

print("\nImporting files (this may take a while)...")
# Import Files to the RagCorpus
try:
    rag.import_files(
        rag_corpus.name,
        paths,
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,
                chunk_overlap=100,
            ),
        ),
        max_embedding_requests_per_min=500,  # Reduced rate for stability
    )
    print("Files imported successfully!")
except Exception as e:
    print(f"Import failed: {e}")
    print("You may need to wait and retry, or import in smaller batches")
    exit(1)

print("\nTesting direct retrieval...")
# Direct context retrieval
rag_retrieval_config = rag.RagRetrievalConfig(
    top_k=3,
    filter=rag.Filter(vector_distance_threshold=0.5),
)

response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=rag_corpus.name,
        )
    ],
    text="What information is in these documents?",
    rag_retrieval_config=rag_retrieval_config,
)
print("Retrieval response:")
print(response)

print("\nTesting generation with RAG...")
# Create RAG retrieval tool
rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=rag_corpus.name,
                )
            ],
            rag_retrieval_config=rag_retrieval_config,
        ),
    )
)

# Create Gemini model with RAG
rag_model = GenerativeModel(
    model_name="gemini-2.0-flash-001", tools=[rag_retrieval_tool]
)

# Generate response
response = rag_model.generate_content(
    "Summarize the key information from the documents"
)
print("Generated response:")
print(response.text)
