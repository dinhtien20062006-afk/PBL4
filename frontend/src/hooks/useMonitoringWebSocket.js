import { useState, useEffect, useRef } from 'react';

export const useMonitoringWebSocket = (url = "ws://127.0.0.1:8000/ws/monitoring") => {
    const [trafficData, setTrafficData] = useState([]);
    const [latestAlert, setLatestAlert] = useState(null);
    const ws = useRef(null);

    useEffect(() => {
        let reconnectTimeout;
        const connect = () => {
            ws.current = new WebSocket(url);
            
            ws.current.onopen = () => {
                if (reconnectTimeout) clearTimeout(reconnectTimeout);
            };
            
            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'traffic') {
                    setTrafficData(prev => {
                        const newData = [...prev, data.payload];
                        return newData.length > 20 ? newData.slice(newData.length - 20) : newData;
                    });
                } else if (data.type === 'alert') {
                    setLatestAlert(data.payload);
                }
            };
            
            ws.current.onclose = () => {
                reconnectTimeout = setTimeout(connect, 3000);
            };
            
            ws.current.onerror = () => ws.current.close();
        };
        
        connect();
        
        return () => {
            if (ws.current) ws.current.close();
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
        };
    }, [url]);

    return { trafficData, latestAlert };
};