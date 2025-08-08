"use client";
import { useState } from 'react';
import { DataUpload } from '@/components/DataUpload';
import { Dashboard } from '@/components/Dashboard';
import { Header } from '@/components/Header';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'dashboard'>('upload');

  const handleDataUploaded = (newSessionId: string) => {
    setSessionId(newSessionId);
    setCurrentStep('dashboard');
  };

  const handleReset = () => {
    setSessionId(null);
    setCurrentStep('upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header onReset={handleReset} />
      <main className="container mx-auto px-4 py-8">
        {currentStep === 'upload' && (
          <DataUpload onDataUploaded={handleDataUploaded} />
        )}
        {currentStep === 'dashboard' && sessionId && (
          <Dashboard sessionId={sessionId} onBack={handleReset} />
        )}
      </main>
    </div>
  );
}
