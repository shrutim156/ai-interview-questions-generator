import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function QuestionCard({
  index,
  questionItem,
  sessionId,
  onFetchAnswer,
  onFetchCode,
}) {
  const [showAnswer, setShowAnswer] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [loadingCode, setLoadingCode] = useState(false);
  const [answerError, setAnswerError] = useState(null);
  const [codeError, setCodeError] = useState(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(questionItem.question);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleAnswer = async () => {
    if (showAnswer) {
      setShowAnswer(false);
      return;
    }

    setShowAnswer(true);

    if (!questionItem.model_answer) {
      setLoadingAnswer(true);
      setAnswerError(null);
      try {
        await onFetchAnswer(sessionId, questionItem.id);
      } catch (err) {
        setAnswerError(err.message || 'Error fetching answer');
      } finally {
        setLoadingAnswer(false);
      }
    }
  };

  const handleToggleCode = async () => {
    if (showCode) {
      setShowCode(false);
      return;
    }

    setShowCode(true);

    if (!questionItem.code_example) {
      setLoadingCode(true);
      setCodeError(null);
      try {
        await onFetchCode(sessionId, questionItem.id);
      } catch (err) {
        setCodeError(err.message || 'Error fetching code sample');
      } finally {
        setLoadingCode(false);
      }
    }
  };

  return (
    <div className="question-card">
      <div className="q-header">
        <span className="q-index">{index + 1}</span>
        <div style={{ flex: 1 }}>
          <p className="q-title">{questionItem.question}</p>
          {questionItem.hint && (
            <div className="q-hint-inline">
              💡 <strong>Hint:</strong> {questionItem.hint}
            </div>
          )}
        </div>
        <button className="icon-btn" onClick={handleCopy} title="Copy Question">
          {copied ? '✓' : '📋'}
        </button>
      </div>

      <div className="q-actions">
        <button
          type="button"
          className="action-btn-secondary"
          onClick={handleToggleAnswer}
          disabled={loadingAnswer}
        >
          {loadingAnswer
            ? 'Generating Answer...'
            : showAnswer
            ? 'Hide Answer ▲'
            : 'Show Answer ▼'}
        </button>

        <button
          type="button"
          className="action-btn-secondary"
          onClick={handleToggleCode}
          disabled={loadingCode}
        >
          {loadingCode
            ? 'Generating Code...'
            : showCode
            ? 'Hide Code Example ▲'
            : 'Show Code Example ▼'}
        </button>
      </div>

      {showAnswer && (
        <div className="q-answer-container">
          {loadingAnswer && <div className="card-loader">Fetching model answer...</div>}
          {answerError && <div className="card-error">{answerError}</div>}
          {questionItem.model_answer && (
            <div className="q-answer markdown-body">
              <strong className="answer-header">Model Answer:</strong>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {questionItem.model_answer}
              </ReactMarkdown>
            </div>
          )}
        </div>
      )}

      {showCode && (
        <div className="q-code-container">
          {loadingCode && <div className="card-loader">Fetching code snippet...</div>}
          {codeError && <div className="card-error">{codeError}</div>}
          {questionItem.code_example && (
            <pre className="q-code">
              <code>{questionItem.code_example}</code>
            </pre>
          )}
        </div>
      )}
    </div>
  );
}