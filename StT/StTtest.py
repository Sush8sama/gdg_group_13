from google.cloud import speech

client = speech.SpeechClient()

gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

def transcribe_speech():
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # operation = client.long_running_recognize(config=config, audio=audio)

    # print("Waiting for operation to complete...")
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

transcribe_speech()