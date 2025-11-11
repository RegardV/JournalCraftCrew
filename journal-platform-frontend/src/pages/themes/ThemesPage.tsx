import React from 'react';
import { ArrowLeftIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';

const ThemesPage: React.FC = () => {
  const themes = [
    { name: 'Mindfulness', description: 'Cultivate awareness and inner peace', icon: '🧘' },
    { name: 'Productivity', description: 'Achieve your goals and stay focused', icon: '🎯' },
    { name: 'Gratitude', description: 'Practice thankfulness and positivity', icon: '🙏' },
    { name: 'Creativity', description: 'Unlock your artistic potential', icon: '🎨' },
    { name: 'Fitness', description: 'Track your health and wellness journey', icon: '💪' },
    { name: 'Learning', description: 'Document your educational growth', icon: '📚' },
  ];

  return (
    <div className="min-h-screen gradient-bg">
      <div className="section-container py-8">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => window.history.back()}
            className="mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back
          </Button>

          <h1 className="text-4xl font-bold gradient-text mb-2">Journal Themes</h1>
          <p className="text-lg text-gray-600">Choose a theme that inspires your journaling journey</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {themes.map((theme) => (
            <div
              key={theme.name}
              className="glass-effect rounded-2xl border border-color-border p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
              onClick={() => window.location.href = '/dashboard'}
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-color-primary to-color-primary-dark rounded-xl flex items-center justify-center text-2xl">
                  {theme.icon}
                </div>
                <h3 className="text-lg font-semibold">{theme.name}</h3>
              </div>
              <p className="text-gray-600">{theme.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-3 p-6 bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl border border-amber-200">
            <SparklesIcon className="h-8 w-8 text-amber-600" />
            <div className="text-left">
              <p className="font-semibold text-amber-800">Need something custom?</p>
              <p className="text-sm text-amber-600">Create personalized themes with AI assistance</p>
            </div>
            <Button onClick={() => window.location.href = '/dashboard'}>
              Try Now
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemesPage;