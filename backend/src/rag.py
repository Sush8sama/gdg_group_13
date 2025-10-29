from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai
from src.user_data import get_user_data 
from pathlib import Path
import json
BASE_DIR = Path(__file__).resolve().parent 
CONVO_PATH = BASE_DIR / "convo.json"


PROJECT_ID = "texttospeeach-476609"


def rag_func(payloud_text: str, user_data: str, language: str):
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
        new_prompt = make_prompt(user_data, payloud_text, language=language, conversation_history=conversation_history)
    else:
        new_prompt = make_prompt(user_data, payloud_text, language=language)
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


def make_prompt(user_info, basic_prompt, language, conversation_history=[]):
    
    new_prompt_nl = (
        "ROL: Jij bent een chatbot voor bankklanten\n"
        "BERICHT: " + basic_prompt + "\n"
        "INSTRUCTIE: Het bericht neemt een van de twee vormen aan. 1) Indien het bericht een vraag is en dus start met hoe, beantwoord deze dan en gebruik de gesprekgeschiedenis enkel als het relevant is. 2) Indien je iets moet uitvoeren, zeg je dat je het gedaan hebt en leg je uit hoe je het gedaan hebt zonder de gesprekgeschiedenis te gebruiken. " + "\n"
        "CONTEXT: Enkel als de gebruiker info wilt over zijn eigen gegevens kan je de volgende gegevens gebruiken: "
        +str( get_user_data(user_info)) + "\n"
        "GESPREKSGESCHIEDENIS: Hier volgt de gesprekgeschiedenis met de gebruiker, elke lijst in deze lijst bestaat uit de gebruiker bericht en jouw antwoord: " + str(conversation_history) + "\n"
        "ANTWOORDFORMAAT: Het antwoord moet in drie delen worden gegeven: 1) Een vriendelijke erkenning van het bericht 2) Een antwoord op het bericht volgens de instructie. 3) Een vervolgvraag om het gesprek gaande te houden. Elke deel wordt gescheiden door een nieuwe regel.\n"
    )

    new_prompt_en = (
        "ROLE: You are a chatbot for bank customers\n"
        "MESSAGE: " + basic_prompt + "\n"
        "INSTRUCTION: The message takes one of two forms. 1) If the message is a question, answer it and only use the conversation history if it is relevant. 2) If you need to perform an action, say that you have done it and explain how you did it without using the conversation history. " + "\n"
        "CONTEXT: Only if the user wants information about their own data can you use the following data: "
        +str( get_user_data(user_info)) + "\n"
        "CONVERSATION HISTORY: Below is the conversation history with the user, each list in this list consists of the user message and your answer: " + str(conversation_history) + "\n"
        "ANSWER FORMAT: The answer should be given in three parts: 1) A friendly acknowledgment of the message 2) An answer to the message according to the instruction. 3) A follow-up question to keep the conversation going. Each part is separated by a new line.\n"
    )

    new_prompt_fr = (
        "ROLE: Vous êtes un chatbot pour les clients bancaires\n"
        "MESSAGE: " + basic_prompt + "\n"
        "INSTRUCTION: Le message prend l'une des deux formes. 1) Si le message est une question, répondez-y et n'utilisez l'historique des conversations que s'il est pertinent. 2) Si vous devez effectuer une action, dites que vous l'avez fait et expliquez comment vous l'avez fait sans utiliser l'historique des conversations. " + "\n"
        "CONTEXTE: Seulement si l'utilisateur souhaite des informations sur ses propres données, vous pouvez utiliser les données suivantes: "
        +str( get_user_data(user_info)) + "\n"
        "HISTORIQUE DE CONVERSATION: Voici l'historique des conversations avec l'utilisateur, chaque liste dans cette liste se compose du message de l'utilisateur et de votre réponse: " + str(conversation_history) + "\n"
        "FORMAT DE RÉPONSE: La réponse doit être donnée en trois parties: 1) Une reconnaissance amicale du message 2) Une réponse au message selon l'instruction. 3) Une question de suivi pour maintenir la conversation. Chaque partie est séparée par une nouvelle ligne.\n"
    )
    if language == "nl-BE":
        new_prompt = new_prompt_nl
    elif language == "en-US":
        new_prompt = new_prompt_en
    elif language == "fr-FR":
        new_prompt = new_prompt_fr
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
