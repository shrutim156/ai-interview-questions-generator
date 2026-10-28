import React, { useState } from 'react';
import Navbar from './components/Navbar';
import QuestionCard from './components/QuestionCard';
import { fetchQuestions, fetchAnswer, fetchCode } from './services/api';
import './App.css';

const PRESET_TOPICS = ["Python", "DSA", "SQL", "System Design", "ML"];
const PRESET_ROLES = [
  "General Software Engineer", 
  "Backend Developer", 
  "Frontend Engineer", 
  "Machine Learning Engineer", 
  "Full Stack Developer"
];

export default function App() {
  const [topic, setTopic] = useState('');
  const [targetRole, setTargetRole] = useState('General Software Engineer');
  const [difficulty, setDifficulty] = useState('Beginner');
  const [numQuestions, setNumQuestions] = useState(5);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setError(null);
    setCopied(false);

    try {
      const data = await fetchQuestions({
        topic: topic.trim(),
        target_role: targetRole,
        difficulty,
        num_questions: parseInt(numQuestions, 10) || 5,
      });

      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchAnswer = async (sessionId, questionId) => {
    const res = await fetchAnswer(sessionId, questionId);
    setResults((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        questions: prev.questions.map((q) =>
          q.id === questionId ? { ...q, model_answer: res.model_answer } : q
        ),
      };
    });
  };

  const handleFetchCode = async (sessionId, questionId) => {
    const res = await fetchCode(sessionId, questionId);
    setResults((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        questions: prev.questions.map((q) =>
          q.id === questionId ? { ...q, code_example: res.code_example } : q
        ),
      };
    });
  };

  const handleCopyAll = () => {
    if (!results?.questions) return;
    const text = results.questions.map((q, i) => `${i + 1}. ${q.question}`).join('\n\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleResetSession = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <Navbar onReset={handleResetSession} />

      <div className="container">
        <header className="header">
          <h1>Generate Tailored Technical Interview Questions</h1>
          <p>Customize target domain, difficulty, question volume, solution hints, and target job roles.</p>
        </header>

        <main className="layout">
          <form className="form-card" onSubmit={handleSubmit}>
            <div className="form-section-title">Configuration</div>

            <div className="form-group">
              <label>TECHNICAL TOPIC</label>
              <div className="chips">
                {PRESET_TOPICS.map((item) => (
                  <button
                    type="button"
                    key={item}
                    className={`chip ${topic === item ? 'active' : ''}`}
                    onClick={() => setTopic(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter your subject"
                required
                style={{ marginTop: '0.5rem' }}
              />
            </div>

            <div className="form-group">
              <label>TARGET ROLE / CONTEXT</label>
              <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
                {PRESET_ROLES.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>DIFFICULTY LEVEL</label>
              <div className="difficulty-toggle">
                {['Beginner', 'Intermediate', 'Advanced'].map((lvl) => (
                  <button
                    type="button"
                    key={lvl}
                    className={`diff-btn ${difficulty === lvl ? 'active' : ''}`}
                    onClick={() => setDifficulty(lvl)}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>NUMBER OF QUESTIONS</label>
              <input
                type="number"
                min="1"
                max="30"
                value={numQuestions}
                onChange={(e) => setNumQuestions(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Generating Questions...' : 'Generate Questions'}
            </button>
          </form>

          <section className="results-section">
            {error && <div className="error-banner">{error}</div>}

            {results && (
              <div className="results-top-bar">
                <div>
                  <h3>{results.topic} <span className="badge-tag">{results.difficulty}</span></h3>
                  <span className="sub-info">Target Role: {results.target_role}</span>
                </div>
                <div className="action-buttons">
                  <button onClick={handleCopyAll} className="action-btn">
                    {copied ? '✓ Copied All' : 'Copy All'}
                  </button>
                  <button onClick={() => setResults(null)} className="action-btn">
                    Refresh
                  </button>
                </div>
              </div>
            )}

            {loading && (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Consulting Gemini AI for targeted technical questions...</p>
              </div>
            )}

            {!loading && results && (
              <div className="questions-list">
                {results.questions.map((item, idx) => (
                  <QuestionCard
                    key={item.id}
                    index={idx}
                    questionItem={item}
                    sessionId={results.session_id}
                    onFetchAnswer={handleFetchAnswer}
                    onFetchCode={handleFetchCode}
                  />
                ))}
              </div>
            )}

            {!loading && !results && !error && (
              <div className="empty-workspace">
                <div className="empty-icon">💡</div>
                <h3>Ready to construct your interview session</h3>
                <p>Configure your topic, role, and difficulty on the left, then click <strong>Generate Questions</strong>.</p>
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}