import React, { useState } from 'react';

const DNALoader = () => (
  <div className="flex items-center justify-center gap-1.5 h-6">
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <div key={i} className="relative w-1.5 h-5 flex-shrink-0">
        <div className="absolute top-[2px] bottom-[2px] left-1/2 w-[2px] bg-gray-600/50 -translate-x-1/2" />
        <div
          className="w-1.5 h-1.5 bg-white rounded-full dna-dot-top absolute top-0"
          style={{ animationDelay: `${i * -0.2}s` }}
        />
        <div
          className="w-1.5 h-1.5 bg-gray-400 rounded-full dna-dot-bottom absolute bottom-0"
          style={{ animationDelay: `${i * -0.2}s` }}
        />
      </div>
    ))}
  </div>
);

const StoryInput = ({ onGenerate, onUpload, isLoading }) => {
  const [activeTab, setActiveTab] = useState('generate');

  // Generate State
  const [idea, setIdea] = useState('');
  const [genre, setGenre] = useState('Sci-Fi');

  // Upload State
  const [scriptText, setScriptText] = useState('');

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => setScriptText(e.target.result);
    reader.readAsText(file);
  };

  return (
    <div className="relative p-8 bg-white text-gray-900 rounded-xl shadow-xl border border-gray-200">
      <div className="absolute top-6 right-8 text-xs font-mono text-gray-400">
        v2.1
      </div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 text-black">
          Narrative DNA Engine
        </h2>
        <p className="text-sm text-gray-500">
          Decode the genetic architecture of your story — every great narrative shares the same code.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex w-full border-b border-gray-200 mb-6 font-medium">
        <button
          className={`flex-1 text-center pb-3 px-4 transition-colors ${activeTab === 'generate' ? 'border-b-2 border-black text-black' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('generate')}
        >
          Story Title & Synopsis
        </button>
        <button
          className={`flex-1 text-center pb-3 px-4 transition-colors ${activeTab === 'upload' ? 'border-b-2 border-black text-black' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Existing Script
        </button>
      </div>

      {activeTab === 'generate' && (
        <div className="space-y-4 animate-fade-in">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Genre</label>
            <select
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              className="w-full p-3 bg-gray-50 rounded border border-gray-300 focus:border-black outline-none text-black transition-colors"
            >
              <option>Sci-Fi</option>
              <option>Thriller</option>
              <option>Romance</option>
              <option>Horror</option>
              <option>Fantasy</option>
              <option>Mystery</option>
              <option>Drama</option>
              <option>Comedy</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">What is your story about?</label>
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              className="w-full p-3 h-32 bg-gray-50 rounded border border-gray-300 focus:border-blue-500 outline-none text-black placeholder-gray-400"
              placeholder="e.g. 'The Matrix' - A hacker discovers his entire reality is a computer simulation..."
            />
          </div>
          <button
            onClick={() => onGenerate(idea, genre)}
            disabled={isLoading || !idea.trim()}
            className="w-full py-4 bg-black text-white hover:bg-gray-800 rounded font-bold text-lg transition-all flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <DNALoader />
            ) : (
              "Generate Narrative Arc"
            )}
          </button>
        </div>
      )}

      {activeTab === 'upload' && (
        <div className="space-y-4 animate-fade-in">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload File (.txt) or Paste Script Below</label>
            <input
              type="file"
              accept=".txt"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 mb-4
                file:mr-4 file:py-2 file:px-4
                file:rounded file:border-0
                file:text-sm file:font-semibold
                file:bg-gray-100 file:text-black
                hover:file:bg-gray-200 cursor-pointer"
            />
            <textarea
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              className="w-full p-3 h-48 bg-gray-50 rounded border border-gray-300 focus:border-purple-500 outline-none text-black placeholder-gray-400"
              placeholder="INT. ROOM - DAY&#10;&#10;JOHN enters the room quickly..."
            />
          </div>
          <button
            onClick={() => onUpload(scriptText)}
            disabled={isLoading || !scriptText.trim()}
            className="w-full py-4 bg-black text-white hover:bg-gray-800 rounded font-bold text-lg transition-all flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="animate-pulse">Analyzing...</span>
            ) : (
              "Analyze Script"
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default StoryInput;
