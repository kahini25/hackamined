import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const CharacterGraph = ({ data }) => {
    const svgRef = useRef();

    useEffect(() => {
        // Expected data format: { interaction_graph: { nodes: [{id, group}], edges: [{source, target, weight}] } }
        if (!data || !data.interaction_graph?.nodes || data.interaction_graph.nodes.length === 0) return;

        // Use specific width and height that fit the container
        const width = 400;
        const height = 300;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove(); // Clear previous rendering

        // Add a container group and center it slightly
        const g = svg.append("g");

        // Initialize the simulation
        const simulation = d3.forceSimulation(data.interaction_graph.nodes)
            .force("link", d3.forceLink(data.interaction_graph.edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(30));

        // Draw Links (edges)
        const link = g.append("g")
            .attr("stroke", "#4B5563") // text-gray-600
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(data.interaction_graph.edges)
            .join("line")
            .attr("stroke-width", d => Math.max(1, d.weight * 1.5)); // Scale edge thickness by weight

        // Draw Nodes
        const node = g.append("g")
            .attr("stroke", "#1F2937") // text-gray-800
            .attr("stroke-width", 2)
            .selectAll("circle")
            .data(data.interaction_graph.nodes)
            .join("circle")
            .attr("r", 15)
            .attr("fill", "#8B5CF6") // Tailwind purple-500
            .call(drag(simulation));

        // Draw Text Labels
        const labels = g.append("g")
            .selectAll("text")
            .data(data.interaction_graph.nodes)
            .join("text")
            .attr("dy", -20) // Above the node
            .attr("text-anchor", "middle")
            .text(d => d.id)
            .attr("fill", "#E5E7EB") // text-gray-200
            .attr("font-size", "12px")
            .attr("font-weight", "500")
            .attr("pointer-events", "none");

        // Simulation tick updates
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x = Math.max(15, Math.min(width - 15, d.x)))
                .attr("cy", d => d.y = Math.max(15, Math.min(height - 15, d.y)));

            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });

        // Drag behavior definition
        function drag(simulation) {
            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }

            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }

            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }

        // Cleanup on unmount
        return () => {
            simulation.stop();
        };

    }, [data]);

    if (!data || !data.interaction_graph?.nodes || data.interaction_graph.nodes.length === 0) {
        return (
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-full flex flex-col justify-center items-center text-gray-500 text-sm">
                <h3 className="text-gray-400 text-sm mb-2 uppercase tracking-wider w-full text-left">Character Graph</h3>
                <p>No character interactions detected in this segment.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-full">
            <h3 className="text-gray-400 text-sm mb-2 uppercase tracking-wider">Character Interactions</h3>
            <div className="flex justify-center w-full">
                <svg ref={svgRef} viewBox="0 0 400 300" className="w-full h-auto max-w-sm"></svg>
            </div>
        </div>
    );
};

export default CharacterGraph;
