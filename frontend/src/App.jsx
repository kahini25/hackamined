import React, { useState } from 'react';
import StoryInput from './components/StoryInput';
import EpisodeDashboard from './components/EpisodeDashboard';
import { generateArc } from './api';

function App() {
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (idea, genre) => {
    setLoading(true);
    try {
      const data = await generateArc(idea, genre);
      setEpisodes(data.episodes);
    } catch (error) {
      const msg = error?.response?.data?.detail || error?.message || "Unknown error";
      alert(`⚠️ Generation failed:\n\n${msg}`);
    }
    setLoading(false);
  };

  const handleUpload = (scriptText) => {
    // Treat the uploaded script as one single "Episode" segment
    const uploadedEp = {
      title: "Uploaded Script",
      synopsis: "Custom script uploaded for direct analysis.",
      script_segment: scriptText
    };
    setEpisodes([uploadedEp]);
  };

  const handleReset = () => {
    setEpisodes([]);
  };

  return (
    <div className="min-h-screen text-[#6b6560] p-6 font-sans" style={{ backgroundColor: '#f5f0e8' }}>
      <div className="max-w-7xl mx-auto">


        {episodes.length === 0 ? (
          <div className="max-w-2xl mx-auto mt-6">
            <div className="mb-8 text-center">
              <h1 className="text-4xl font-black mb-3 uppercase tracking-[-0.03em]" style={{ wordSpacing: '0.35em', color: '#2c2520' }}>
                Narrative DNA <span style={{ color: '#c8bfb0' }}>Engine</span>
              </h1>
              <p className="text-sm leading-relaxed" style={{ color: '#9c9088' }}>
                Decode the genetic architecture of your story.
              </p>
            </div>
            <StoryInput onGenerate={handleGenerate} onUpload={handleUpload} isLoading={loading} />
          </div>
        ) : (
          <EpisodeDashboard episodes={episodes} onReset={handleReset} />
        )}
      </div>
    </div>
  );
}

export default App;
