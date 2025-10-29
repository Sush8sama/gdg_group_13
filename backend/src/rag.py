from vertexai.generative_models import GenerativeModel, Tool
import vertexai
PROJECT_ID = "texttospeeach-476609"



def rag_func(payloud_text: str):
    vertexai.init(project=PROJECT_ID, location="europe-west1")


    # Get existing corpora
    corpora_pager = vertexai.rag.list_corpora()
    corpora = list(corpora_pager)  # Convert to list

    print("Available corpora:")
    for i, corpus in enumerate(corpora):
        print(f"  {i}. {corpus.display_name}: {corpus.name}")

    # Use the most recent corpus (last one in the list)
    corpus_name = corpora[-1].name  # Use the last created corpus
    # Or manually select: corpus_name = "projects/texttospeeach-476609/locations/europe-west3/ragCorpora/6917529027641081856"

    print(f"\nUsing corpus: {corpus_name}")

    # Configure retrieval
    rag_retrieval_config = vertexai.rag.RagRetrievalConfig(
        top_k=5,
        filter=vertexai.rag.Filter(vector_distance_threshold=0.5),
    )

    # Test direct retrieval
    print("\n1. Testing direct retrieval...")
    response = vertexai.rag.retrieval_query(
        rag_resources=[
            vertexai.rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=payloud_text,
        rag_retrieval_config=rag_retrieval_config,
    )

    print(f"Retrieved {len(response.contexts.contexts)} contexts")
    for i, context in enumerate(response.contexts.contexts[:3]):
        print(f"\nContext {i + 1}:")
        print(f"  Source: {context.source_display_name}")
        print(f"  Score: {context.score:.3f}")
        print(f"  Text preview: {context.text[:200]}...")

    # Create RAG retrieval tool
    print("\n2. Setting up RAG model...")
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=vertexai.rag.Retrieval(
            source=vertexai.rag.VertexRagStore(
                rag_resources=[
                    vertexai.rag.RagResource(
                        rag_corpus=corpus_name,
                    )
                ],
                rag_retrieval_config=rag_retrieval_config,
            ),
        )
    )

    # Use gemini-1.5-flash (available in europe-west3)
    rag_model = GenerativeModel(model_name="gemini-2.0-flash", tools=[rag_retrieval_tool])

    # Generate response
    print("\n3. Generating response with RAG...")
    #response = GenerativeModel(model_name="gemini-2.5-flash").generate_content(payloud_text)
    response = rag_model.generate_content(payloud_text)
    print("Generated response:")
    return response
    # print("\nGenerated response:")
    # print(response.text)

    # # Clean up old corpora if needed
    # print("\n" + "=" * 60)
    # print("Note: You have 3 corpora with the same name. To delete old ones:")
    # print("To delete a corpus, use:")
    # for i, corpus in enumerate(corpora[:-1]):  # All except the last one
    #     print(f"  vertexai.rag.delete_corpus(name='{corpus.name}')")
