import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './TrafficChart.css';

const TrafficChart = ({ data }) => {
    return (
        <div className="traffic-chart-container" style={{ height: '350px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis dataKey="time" stroke="#888" tick={{ fill: '#888' }} />
                    <YAxis stroke="#888" tick={{ fill: '#888' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e1e1e', border: 'none', color: '#fff' }} />
                    <Line 
                        type="monotone" 
                        dataKey="packets" 
                        stroke="#00ffcc" 
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={false} 
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TrafficChart;