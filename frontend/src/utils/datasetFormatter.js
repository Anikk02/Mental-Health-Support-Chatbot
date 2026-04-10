export function toDatasetPayload({ userId, text, extra = {} }) {
  const inputText = (text || "").trim();
  const inputLength = inputText ? inputText.split(/\s+/).length : 0;
  return {
    user_id: userId ? String(userId) : None,
    user_input: inputText,
    emotion_labels: extra.emotion_labels || "none",
    user_sentiment: extra.user_sentiment !== undefined ? extra.user_sentiment : 0.0,
    trigger_word: extra.trigger_word || "none",
    response_empathy_score: extra.response_empathy_score || 0.0,
    risky_term_count: extra.risky_term_count || 0,
    risk_intensity_score: extra.risk_intensity_score || 0.0,
    input_length: inputLength,
    output_length: extra.output_length || 120,
    safety_flag: extra.safety_flag || 0
  };
}
