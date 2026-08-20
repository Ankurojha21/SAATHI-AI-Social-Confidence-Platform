import { create } from "zustand";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const useChatStore = create((set, get) => ({
  // ============================================================
  // SARA / AI COMPANION
  // ============================================================

  companionMessages: [],
  companionLoading: false,
  lastSentiment: null,
  companionError: null,

  // ============================================================
  // SEND MESSAGE TO SARA
  // ============================================================

  sendCompanionMessage: async (message, options = {}) => {
  const text = typeof message === "string"
    ? message.trim()
    : "";

  if (!text) return null;

  const { isVoiceMode = false } = options;

  const currentMessages = get().companionMessages || [];

  const userMessage = {
    role: "user",
    content: text,
    timestamp: new Date().toISOString(),
    isVoiceMode,
  };

  const updatedMessages = [
    ...currentMessages,
    userMessage,
  ];

  set({
    companionMessages: updatedMessages,
    companionLoading: true,
    companionError: null,
  });

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: updatedMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
          is_voice_mode: isVoiceMode,
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();

      throw new Error(
        `Chat request failed: ${response.status} ${errorText}`
      );
    }

    const data = await response.json();

    const saraResponse =
      data.reply ||
      data.response ||
      data.message ||
      "I'm here with you. Tell me a little more.";

    const saraMessage = {
      role: "assistant",
      content: saraResponse,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      companionMessages: [
        ...state.companionMessages,
        saraMessage,
      ],

      companionLoading: false,

      lastSentiment:
        data.sentiment ||
        state.lastSentiment,

    }));

    return data;

  } catch (error) {
    console.error("Sara conversation error:", error);

    set({
      companionLoading: false,
      companionError: error.message,
    });

    return null;
  }
},

  // ============================================================
  // STANDALONE SENTIMENT ANALYSIS
  // ============================================================

  analyzeSentiment: async (
    text,
    source = "chat"
  ) => {
    if (!text?.trim()) return null;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/sentiment`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: text.trim(),
            source,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Sentiment request failed: ${response.status}`
        );
      }

      const data = await response.json();

      set({
        lastSentiment: data,
      });

      return data;

    } catch (error) {
      console.error(
        "SaraSense error:",
        error
      );

      return null;
    }
  },

  // ============================================================
  // CLEAR SARA CONVERSATION
  // ============================================================

  clearCompanionMessages: () => {
    set({
      companionMessages: [],
      lastSentiment: null,
      companionError: null,
    });
  },

  // ============================================================
  // CLEAR ERROR
  // ============================================================

  clearCompanionError: () => {
    set({
      companionError: null,
    });
  },
}));

export default useChatStore;
export { useChatStore };  