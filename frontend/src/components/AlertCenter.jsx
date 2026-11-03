import React, { useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useMonitoringWebSocket } from '../hooks/useMonitoringWebSocket';
import './AlertCenter.css';

const AlertCenter = () => {
    const { latestAlert } = useMonitoringWebSocket();

    useEffect(() => {
        if (latestAlert) {
            toast.error(
                <div>
                    <strong>🚨 TẤN CÔNG MỚI!</strong>
                    <div style={{ fontSize: '13px', marginTop: '5px' }}>
                        IP: {latestAlert.ip} <br/>
                        Loại: {latestAlert.attack_type}
                    </div>
                </div>,
                {
                    position: "top-right",
                    autoClose: 5000,
                    className: "blinking-red-toast"
                }
            );
        }
    }, [latestAlert]);

    return (
        <div className="alert-center-container">
            <ToastContainer />
            {/* Giữ nguyên phần render danh sách cảnh báo cũ của bạn ở đây */}
            <h3>Trung tâm Cảnh báo</h3>
        </div>
    );
};

export default AlertCenter;