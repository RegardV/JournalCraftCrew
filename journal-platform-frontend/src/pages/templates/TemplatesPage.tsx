import React from 'react';
import { ArrowLeftIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';

const TemplatesPage: React.FC = () => {
  const templates = [
    {
      name: 'Daily Reflection',
      description: 'Capture thoughts and experiences from your day',
      icon: '📔',
      category: 'Personal'
    },
    {
      name: 'Goal Tracker',
      description: 'Monitor progress towards your objectives',
      icon: '🎯',
      category: 'Productivity'
    },
    {
      name: 'Gratitude Log',
      description: 'Practice daily thankfulness',
      icon: '🙏',
      category: 'Wellness'
    },
    {
      name: 'Mood Tracker',
      description: 'Monitor emotional patterns over time',
      icon: '😊',
      category: 'Mental Health'
    },
    {
      name: 'Habit Builder',
      description: 'Develop and maintain positive habits',
      icon: '✅',
      category: 'Personal Growth'
    },
    {
      name: 'Creative Writing',
      description: 'Express your artistic side',
      icon: '✍️',
      category: 'Creative'
    },
  ];

  const categories = ['All', 'Personal', 'Productivity', 'Wellness', 'Mental Health', 'Personal Growth', 'Creative'];

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

          <h1 className="text-4xl font-bold gradient-text mb-2">Journal Templates</h1>
          <p className="text-lg text-gray-600">Start with proven structures for effective journaling</p>
        </div>

        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Button
                key={category}
                variant={category === 'All' ? 'primary' : 'outline'}
                size="sm"
              >
                {category}
              </Button>
            ))}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <div
              key={template.name}
              className="glass-effect rounded-2xl border border-color-border p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
              onClick={() => window.location.href = '/dashboard'}
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-color-primary to-color-primary-dark rounded-xl flex items-center justify-center text-2xl">
                  {template.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{template.name}</h3>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    {template.category}
                  </span>
                </div>
              </div>
              <p className="text-gray-600">{template.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-3 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl border border-purple-200">
            <DocumentTextIcon className="h-8 w-8 text-purple-600" />
            <div className="text-left">
              <p className="font-semibold text-purple-800">Create custom templates</p>
              <p className="text-sm text-purple-600">Design personalized journal structures with AI</p>
            </div>
            <Button onClick={() => window.location.href = '/dashboard'}>
              Create Template
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplatesPage;