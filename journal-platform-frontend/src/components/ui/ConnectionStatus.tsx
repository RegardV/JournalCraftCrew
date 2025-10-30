// Connection Status Component

import React, { useState, useEffect } from 'react';
import { systemAPI } from '@/lib/api';

export default function ConnectionStatus() {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const health = await systemAPI.getHealth();
        if (health.status === 'healthy') {
          setStatus('connected');
        } else {
          setStatus('disconnected');
        }
      } catch (error) {
        setStatus('disconnected');
      }
      setLastCheck(new Date());
    };

    // Check connection immediately
    checkConnection();

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-green-500';
      case 'disconnected':
        return 'bg-red-500';
      case 'checking':
        return 'bg-yellow-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'checking':
        return 'Checking...';
    }
  };

  return (
    <div className="fixed top-6 right-6 z-50">
      <div className="glass-effect rounded-2xl shadow-lg px-4 py-3 flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${status === 'connected' ? 'animate-pulse' : ''}`}></div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-color-text">{getStatusText()}</span>
          {lastCheck && (
            <span className="text-xs text-color-text-light">
              {lastCheck.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}