import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useMonitoringWebSocket } from '../hooks/useMonitoringWebSocket';
import './AlertCenter.css';

const AlertCenter = () => {
    const [alerts, setAlerts] = useState([]);
    const { latestAlert } = useMonitoringWebSocket();

    // 1. Tải danh sách cảnh báo từ Database khi vừa vào trang
    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                // Gọi API backend (cổng 8000)
                const response = await fetch('http://127.0.0.1:8000/api/alerts');
                const data = await response.json();
                if (Array.isArray(data)) setAlerts(data);
            } catch (error) {
                console.error("Lỗi tải danh sách cảnh báo:", error);
            }
        };
        fetchAlerts();
    }, []);

    // 2. Xử lý Real-time: Khi có cảnh báo mới từ WebSocket
    useEffect(() => {
        if (latestAlert) {
            // Hiển thị Toast khẩn cấp nhấp nháy
            toast.error(
                <div>
                    <strong style={{ fontSize: '16px' }}>🚨 PHÁT HIỆN TẤN CÔNG!</strong>
                    <div style={{ marginTop: '8px', fontSize: '14px' }}>
                        <div><b>IP Tấn công:</b> {latestAlert.ip}</div>
                        <div><b>Loại hình:</b> {latestAlert.attack_type}</div>
                        <div><b>Thời gian:</b> {latestAlert.time}</div>
                    </div>
                </div>,
                {
                    position: "top-right",
                    autoClose: 6000,
                    className: "blinking-red-toast"
                }
            );

            // Cập nhật cảnh báo mới lên ĐẦU danh sách bảng
            setAlerts(prevAlerts => [latestAlert, ...prevAlerts]);
        }
    }, [latestAlert]);

    return (
        <div className="alert-center-container">
            <ToastContainer />
            <h3 className="alert-title">Trung tâm Cảnh báo</h3>
            
            <div className="table-responsive">
                <table className="alerts-table">
                    <thead>
                        <tr>
                            <th>Thời gian</th>
                            <th>IP Tấn công</th>
                            <th>Loại tấn công</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alerts.length > 0 ? (
                            alerts.map((alert, index) => (
                                <tr key={index} className="alert-row">
                                    <td>{alert.time || alert.created_at || 'Vừa xong'}</td>
                                    <td className="alert-ip">{alert.ip || alert.ip_address}</td>
                                    <td>{alert.attack_type || alert.reason}</td>
                                    <td>
                                        <button className="btn-block">Chặn IP</button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4" style={{ textAlign: 'center', padding: '20px' }}>
                                    Chưa có dữ liệu cảnh báo.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AlertCenter;