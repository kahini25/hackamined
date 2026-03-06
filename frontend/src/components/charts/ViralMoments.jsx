import React from 'react';

const ViralMoments = ({ moments }) => {
    if (!moments || moments.length === 0) {
        return (
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 h-full text-center text-gray-500">
                <h3 className="text-gray-400 text-sm mb-2 uppercase tracking-wider">Viral Moments</h3>
                <p className="mt-4">No significant viral signals detected.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-gray-400 text-sm mb-6 uppercase tracking-wider flex items-center gap-2">
                <span className="text-purple-500">🔥</span> Top Viral Moments Timeline
            </h3>

            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-purple-500 before:via-pink-500 before:to-gray-800">

                {moments.map((moment, idx) => (
                    <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        {/* Timeline dot */}
                        <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-gray-900 bg-gray-800 text-gray-500 group-hover:text-purple-400 group-hover:bg-gray-900 shadow-md transform transition-transform group-hover:scale-110 absolute left-0 md:left-1/2 -translate-x-1/2 z-10">
                            <span className="font-bold text-xs">{idx + 1}</span>
                        </div>

                        {/* Content Card */}
                        <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-lg bg-gray-900 border border-gray-700 shadow-lg group-hover:border-purple-500/50 transition-colors ml-14 md:ml-0">
                            <div className="flex justify-between items-start mb-2">
                                <span className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-pink-400 bg-pink-400/10 rounded border border-pink-400/20">
                                    {moment.reason}
                                </span>
                                <span className="text-sm font-mono text-gray-400" title="Viral Score">
                                    {moment.score.toFixed(2)}
                                </span>
                            </div>
                            <p className="text-sm text-gray-300 leading-relaxed italic border-l-2 border-purple-500/50 pl-3">
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
