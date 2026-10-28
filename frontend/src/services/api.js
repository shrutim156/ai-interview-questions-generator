export async function fetchQuestions(payload) {
  const response = await fetch('/api/generate-questions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate questions.');
  }
  return response.json();
}

export async function fetchAnswer(sessionId, questionId) {
  const response = await fetch('/api/generate-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question_id: questionId }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate answer.');
  }
  return response.json();
}

export async function fetchCode(sessionId, questionId) {
  const response = await fetch('/api/generate-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question_id: questionId }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate code sample.');
  }
  return response.json();
}