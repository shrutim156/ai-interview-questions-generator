import React from 'react';

const PRESET_TOPICS = [
  "Python", 
  "SQL", 
  "DBMS", 
  "Data Structures", 
  "React.js", 
  "FastAPI", 
  "Machine Learning",
  "Object-Oriented Programming"
];

export default function TopicSelector({ topic, setTopic }) {
  return (
    <div className="form-group">
      <label>Technical Topic</label>
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="e.g. Python OOP, System Design, Docker"
        required
      />
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
    </div>
  );
}
 