import React from 'react';

const RetentionHeatmap = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Helper to get color based on risk (0 to 1)
    const getRiskColor = (risk) => {
        // 0 is green, 1 is bright red
        const r = Math.floor(239 * risk + 34 * (1 - risk)); // max 239, min 34 (Tailwind red-500 approx vs green-500)
        const g = Math.floor(68 * risk + 197 * (1 - risk)); // max 68, min 197
        const b = Math.floor(68 * risk + 94 * (1 - risk));  // max 68, min 94
        return `rgb(${r}, ${g}, ${b})`;
    };

    return (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 w-full">
            <h3 className="text-gray-500 font-semibold text-sm mb-4 uppercase tracking-wider">Retention Drop-off Risk Heatmap</h3>
            <div className="flex w-full h-12 rounded-lg overflow-hidden border border-gray-300 shadow-inner">
                {data.map((segment, idx) => (
                    <div
                        key={idx}
                        className="flex-1 flex flex-col justify-center items-center transition-all hover:opacity-90 cursor-help"
                        style={{ backgroundColor: getRiskColor(segment.drop_off_risk) }}
                        title={`Risk: ${(segment.drop_off_risk * 100).toFixed(0)}%`}
                    >
                        <span className="text-xs font-bold text-white shadow-sm drop-shadow-md">
                            {(segment.drop_off_risk * 100).toFixed(0)}%
                        </span>
                    </div>
                ))}
            </div>
            <div className="flex w-full mt-2 justify-between px-2 text-xs text-gray-500 font-mono">
                {data.map((segment, idx) => (
                    <span key={idx} className="flex-1 text-center">{segment.time_range}</span>
                ))}
            </div>
        </div>
    );
};

export default RetentionHeatmap;
