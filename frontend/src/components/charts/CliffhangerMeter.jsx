import React from 'react';

const CliffhangerMeter = ({ score }) => {
    // Assuming score is 0-100
    const normalizedScore = Math.min(Math.max(score || 0, 0), 100);

    let statusText = "Low Tension";
    let statusColor = "text-gray-400";
    let barColor = "bg-gray-400";

    if (normalizedScore > 75) {
        statusText = "Extreme Cliffhanger";
        statusColor = "text-[#b87060]";
        barColor = "bg-[#b87060]";
    } else if (normalizedScore > 50) {
        statusText = "Solid Hook";
        statusColor = "text-[#c4955a]";
        barColor = "bg-[#c4955a]";
    } else if (normalizedScore > 25) {
        statusText = "Mild Interest";
        statusColor = "text-blue-400";
        barColor = "bg-blue-400";
    }

    return (
        <div className="w-full">
            <h3 className="text-xs font-light text-[#9c9088] uppercase tracking-[0.2em] mb-6 flex justify-between">
                Cliffhanger Strength
                <span className={`font-black ${statusColor}`}>{normalizedScore.toFixed(0)} / 100</span>
            </h3>

            <div className="mt-4">
                <div className="flex justify-between text-[9px] text-[#9c9088] mb-2 w-full font-light uppercase tracking-[0.2em]">
                    <span>Resolving</span>
                    <span className={`${statusColor} font-bold`}>{statusText}</span>
                    <span>Unresolved</span>
                </div>

                {/* Progress bar container */}
                <div className="h-2 w-full bg-[#fafafa] rounded-full overflow-hidden border border-[#f0f0f0]">
                    {/* Animated progress bar fill */}
                    <div
                        className={`h-full ${barColor} transition-all duration-1000 ease-out`}
                        style={{ width: `${normalizedScore}%` }}
                    ></div>
                </div>
            </div>
        </div>
    );
};

export default CliffhangerMeter;
