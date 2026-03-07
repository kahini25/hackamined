import React from 'react';

const ViralMoments = ({ moments }) => {
    if (!moments || moments.length === 0) {
        return (
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 h-full text-center text-gray-500">
                <h3 className="text-gray-500 font-semibold text-sm mb-2 uppercase tracking-wider">Viral Moments</h3>
                <p className="mt-4">No significant viral signals detected.</p>
            </div>
        );
    }

    return (
        <div className="w-full">
            <h3 className="text-xs font-light text-[#9c9088] uppercase tracking-[0.2em] mb-8">
                Narrative Viral Signals
            </h3>

            <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-[#e8e2d8]">

                {moments.map((moment, idx) => (
                    <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        {/* Timeline dot */}
                        <div className="flex items-center justify-center w-8 h-8 rounded-full border border-[#e8e2d8] transition-all absolute left-0 md:left-1/2 -translate-x-1/2 z-10" style={{ backgroundColor: '#faf7f2', color: '#9c9088' }}>
                            <span className="font-mono text-[10px] font-bold">{idx + 1}</span>
                        </div>

                        {/* Content Card */}
                        <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2rem)] p-5 rounded-2xl border transition-all ml-14 md:ml-0" style={{ backgroundColor: '#faf7f2', borderColor: '#e8e2d8' }}>
                            <div className="flex justify-between items-start mb-3">
                                <span className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest rounded border" style={{ color: '#9c9088', backgroundColor: '#f0ebe2', borderColor: '#e0d8cc' }}>
                                    {moment.reason}
                                </span>
                                <span className="text-[10px] font-mono" style={{ color: '#c8bfb0' }} title="Viral Score">
                                    SCORE: {moment.score.toFixed(2)}
                                </span>
                            </div>
                            <p className="text-[#685e54] text-sm leading-relaxed italic border-l pl-4 py-1" style={{ borderColor: '#e8e2d8' }}>
                                "{moment.text}"
                            </p>
                        </div>
                    </div>
                ))}

            </div>
        </div>
    );
};

export default ViralMoments;
