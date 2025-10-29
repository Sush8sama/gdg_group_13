import vertexai
from vertexai.generative_models import GenerativeModel

# Your Google Cloud project ID and location (e.g., "us-central1").
PROJECT_ID = "texttospeeach-476609"
LOCATION = "europe-west2" # e.g., us-central1

# Initialize the Vertex AI SDK with your project and location.
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Load the generative model.
# Note: Model names on Vertex AI can sometimes differ slightly.
# "gemini-1.5-flash-001" is a common name.
model = GenerativeModel(model_name="gemini-2.5-flash")

# Generate content.
response = model.generate_content("Explain how AI works in a few words")

# Print the response.
print(response.text)