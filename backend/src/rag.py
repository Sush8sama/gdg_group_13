from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai
from src.user_data import get_user_data 
from pathlib import Path
import json
BASE_DIR = Path(__file__).resolve().parent 
CONVO_PATH = BASE_DIR / "convo.json"


PROJECT_ID = "texttospeeach-476609"


def rag_func(payloud_text: str, user_data: str):
    vertexai.init(project=PROJECT_ID, location="europe-west1")

    # Get existing corpora
    corpora_pager = rag.list_corpora()
    corpora = list(corpora_pager)  # Convert to list

    print("Available corpora:")
    for i, corpus in enumerate(corpora):
        print(f"  {i}. {corpus.display_name}: {corpus.name}")

    # Use the most recent corpus (last one in the list)
    corpus_name = corpora[-1].name  # Use the last created corpus
    # Or manually select: corpus_name = "projects/texttospeeach-476609/locations/europe-west3/ragCorpora/6917529027641081856"

    print(f"\nUsing corpus: {corpus_name}")

    # Configure retrieval
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=5,
        filter=rag.Filter(vector_distance_threshold=0.5),
    )

    # Test direct retrieval
    print("\n1. Testing direct retrieval...")
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
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
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=corpus_name,
                    )
                ],
                rag_retrieval_config=rag_retrieval_config,
            ),
        )
    )

    # Use gemini-1.5-flash (available in europe-west3)
    rag_model = GenerativeModel(
        model_name="gemini-2.0-flash", tools=[rag_retrieval_tool]
    )

    # Generate response
    print("\n3. Generating response with RAG...")
    # response = GenerativeModel(model_name="gemini-2.5-flash").generate_content(payloud_text)

    if check_convo_user(user_data):
        with open(CONVO_PATH, 'r') as json_file:
            data = json.load(json_file)
        conversation_history = data["conversation"]
        new_prompt = make_prompt(user_data, payloud_text, conversation_history)
    else:
        new_prompt = make_prompt(user_data, payloud_text)
    response = rag_model.generate_content(new_prompt)
    print("Generated response:", response.text)
    update_convo(payloud_text, response.text, user_data)

    return response
    # print("\nGenerated response:")
    # print(response.text)

    # # Clean up old corpora if needed
    # print("\n" + "=" * 60)
    # print("Note: You have 3 corpora with the same name. To delete old ones:")
    # print("To delete a corpus, use:")
    # for i, corpus in enumerate(corpora[:-1]):  # All except the last one
    #     print(f"  rag.delete_corpus(name='{corpus.name}')")


def make_prompt(user_info, basic_prompt, conversation_history=[]):
    new_prompt = (
        "ROL: Jij bent een chatbot voor bankklanten\n"
        "BERICHT: " + basic_prompt + "\n"
        "INSTRUCTIE: Het bericht neemt een van de twee vormen aan. 1) Indien het bericht een vraag is beantwoord deze dan en gebruik de gesprekgeschiedenis enkel als het relevant is. 2) Indien het een bevel is, zeg je dat je het gedaan hebt en leg je uit hoe je het gedaan hebt zonder de gesprekgeschiedenis te gebruiken. " + "\n"
        "CONTEXT: Enkel als de gebruiker info wilt over zijn eigen gegevens kan je de volgende gegevens gebruiken: "
        +str( get_user_data(user_info)) + "\n"
        "GESPREKSGESCHIEDENIS: Hier volgt de gesprekgeschiedenis met de gebruiker, elke lijst in deze lijst bestaat uit de gebruiker bericht en jouw antwoord: " + str(conversation_history) + "\n"
        "ANTWOORDFORMAAT: Het antwoord moet in drie delen worden gegeven: 1) Een vriendelijke erkenning van het bericht 2) Een antwoord op het bericht volgens de instructie. 3) Een vervolgvraag om het gesprek gaande te houden. Elke deel wordt gescheiden door een nieuwe regel.\n"
    )
    print("THIS IS THE FINAL PROMPT:" ,new_prompt)
    return new_prompt

def check_convo_user(user):
    with open(CONVO_PATH, 'r') as json_file:
        data = json.load(json_file)
    field = "user"
    if field not in data:
        return False
    if user != data["user"]:
        return False
    return True

def update_convo(prompt, answer, user):
    print("UPDATING CONVO JSON FILE...")
    with open(CONVO_PATH, 'r') as json_file:
        data = json.load(json_file)
        print("CURRENT CONVO JSON:", data)
    field = "user"
    print("CHECKING IF USER MATCHES...", user)


    if data.get("user") != user or field not in data:
        print("USER DOESN'T MATCH, CREATING NEW CONVO JSON...")
        new_data = {
        "user": user,
        "conversation": [(prompt, answer)]
        }
        with open(CONVO_PATH, 'w') as json_file:
            json.dump(new_data, json_file, indent=4)
        print("CREATED NEW CONVO JSON:", new_data)
    else:
        data["conversation"].append((prompt, answer))
        with open(CONVO_PATH, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    print("UPDATED CONVO JSON:", data)
