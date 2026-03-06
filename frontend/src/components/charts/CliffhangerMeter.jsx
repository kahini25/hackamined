import React from 'react';

const CliffhangerMeter = ({ score }) => {
    // Assuming score is 0-100
    const normalizedScore = Math.min(Math.max(score || 0, 0), 100);

    let statusText = "Low Tension";
    let statusColor = "text-gray-400";
    let barColor = "bg-gray-400";

    if (normalizedScore > 75) {
        statusText = "Extreme Cliffhanger";
        statusColor = "text-red-500";
        barColor = "bg-red-500";
    } else if (normalizedScore > 50) {
        statusText = "Solid Hook";
        statusColor = "text-yellow-500";
        barColor = "bg-yellow-500";
    } else if (normalizedScore > 25) {
        statusText = "Mild Interest";
        statusColor = "text-blue-400";
        barColor = "bg-blue-400";
    }

    return (
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <h3 className="text-gray-400 text-sm mb-2 uppercase tracking-wider flex justify-between">
                Cliffhanger Strength
                <span className={`font-bold ${statusColor}`}>{normalizedScore.toFixed(0)} / 100</span>
            </h3>

            <div className="mt-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1 w-full font-mono">
                    <span>Resolving</span>
                    <span className={`${statusColor} font-bold`}>{statusText}</span>
                    <span>Unresolved</span>
                </div>

                {/* Progress bar container */}
                <div className="h-4 w-full bg-gray-900 rounded-full overflow-hidden border border-gray-700 shadow-inner">
                    {/* Animated progress bar fill */}
                    <div
                        className={`h-full ${barColor} shadow-[0_0_10px_currentColor] transition-all duration-1000 ease-out`}
                        style={{ width: `${normalizedScore}%` }}
                    ></div>
                </div>
            </div>
        </div>
    );
};

export default CliffhangerMeter;
