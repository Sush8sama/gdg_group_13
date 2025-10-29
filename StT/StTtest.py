from google.cloud import speech

client = speech.SpeechClient()

def transcribe_speech():
    # Load audio file from local path
    audio_file_path = "StT/luvvoice.com-20251029-nGLoNX.wav"
    
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        audio_channel_count=2,
        language_code="nl-BE",
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

transcribe_speech()