const translations = {
  "en-US": {
    selectUser: "Select your name (optional)",
    title: "ING Voice Assistant",
    greeting: "Hello",
    welcomeBack: (name: string) =>
      `Welcome back, ${name}! Tap below to speak with your assistant.`,
    welcome:
      "Tap the button below to start speaking with your digital assistant.",
    footer: "© 2025 ING Voice Assistant Prototype",
    buttons: {
      start: "Start Recording",
      stop: "Cancel Recording",
      send: "Send",
      listening: "Listening...",
    },
    placeholders: {
      transcribing: "🎤 Transcribing...",
      thinking: "💭 Assistant is thinking ...",
    },
  },
  "nl-BE": {
    selectUser: "Selecteer je naam (optioneel)",
    title: "ING Spraakassistent",
    greeting: "Hallo",
    welcomeBack: (name: string) =>
      `Welkom terug, ${name}! Tik hieronder om met je assistent te praten.`,
    welcome: "Tik op de knop hieronder om met je digitale assistent te praten.",
    footer: "© 2025 ING Spraakassistent Prototype",
    buttons: {
      start: "Start opname",
      stop: "Annuleer opname",
      send: "Versturen",
      listening: "Luisteren...",
    },
    placeholders: {
      transcribing: "🎤 Transcriberen...",
      thinking: "💭 Assistent is aan het nadenken ...",
    },
  },
  "fr-FR": {
    selectUser: "Sélectionnez votre nom (facultatif)",
    title: "Assistant Vocal ING",
    greeting: "Bonjour",
    welcomeBack: (name: string) =>
      `Bon retour, ${name} ! Appuyez ci-dessous pour parler à votre assistant.`,
    welcome:
      "Appuyez sur le bouton ci-dessous pour parler à votre assistant numérique.",
    footer: "© 2025 Prototype de l’Assistant Vocal ING",
    buttons: {
      start: "Commencer l’enregistrement",
      stop: "Annuler l'enregistrement",
      send: "Envoyer",
      listening: "Écoute...",
    },
    placeholders: {
      transcribing: "🎤 Transcription en cours...",
      thinking: "💭 L’assistant réfléchit ...",
    },
  },
};

export default translations;

export type Language = "en-US" | "nl-BE" | "fr-FR";
