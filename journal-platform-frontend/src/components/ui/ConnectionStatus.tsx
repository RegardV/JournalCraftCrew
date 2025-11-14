// Connection Status Component

import React, { useState, useEffect } from 'react';
import { systemAPI } from '@/lib/api';
import { getApiURL } from '@/lib/apiConfig';

export default function ConnectionStatus() {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        // Use a simple health check with fallback
        const baseURL = getApiURL();

        // First try the health endpoint
        try {
          const health = await systemAPI.getHealth();
          if (health.status === 'healthy') {
            setStatus('connected');
          } else {
            setStatus('disconnected');
          }
        } catch (healthError) {
          // Fallback: try a simple API endpoint
          const response = await fetch(`${baseURL}/health`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            setStatus('connected');
          } else {
            setStatus('disconnected');
          }
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
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg px-4 py-3 flex items-center space-x-3 border border-gray-200">
        <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${status === 'connected' ? 'animate-pulse' : ''}`}></div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-900">{getStatusText()}</span>
          {lastCheck && (
            <span className="text-xs text-gray-500">
              {lastCheck.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}