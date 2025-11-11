import React, { useState, useEffect } from 'react';
import { ArrowLeftIcon, PlusIcon, DocumentIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { projectAPI } from '@/lib/api';
import { Button } from '@/components/ui/Button';

interface Project {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  word_count?: number;
  pages_count?: number;
}

const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const response = await projectAPI.getLLMProjects();
        setProjects(response.projects || []);
      } catch (error) {
        console.error('Failed to load projects:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

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

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">My Journals</h1>
              <p className="text-lg text-gray-600">Your complete collection of AI-generated journals</p>
            </div>
            <Button
              onClick={() => window.location.href = '/dashboard'}
              className="flex items-center gap-2"
            >
              <PlusIcon className="h-4 w-4" />
              Create New Journal
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-color-primary"></div>
            <p className="mt-4 text-gray-600">Loading your journals...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <DocumentIcon className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No journals yet</h3>
            <p className="text-gray-600 mb-6">Start creating your first AI-powered journal!</p>
            <Button
              onClick={() => window.location.href = '/dashboard'}
              className="flex items-center gap-2 mx-auto"
            >
              <PlusIcon className="h-4 w-4" />
              Create Your First Journal
            </Button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <div
                key={project.id}
                className="glass-effect rounded-2xl border border-color-border p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
                onClick={() => window.location.href = '/dashboard'}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-color-primary to-color-primary-dark rounded-xl flex items-center justify-center text-white">
                    <DocumentIcon className="h-6 w-6" />
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    project.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {project.status}
                  </span>
                </div>

                <h3 className="text-lg font-semibold mb-2 line-clamp-2">
                  {project.title}
                </h3>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {project.description}
                </p>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <CalendarIcon className="h-4 w-4" />
                    {new Date(project.created_at).toLocaleDateString()}
                  </div>
                  {project.word_count && (
                    <div>
                      {project.word_count.toLocaleString()} words
                    </div>
                  )}
                </div>

                {project.pages_count && (
                  <div className="mt-2 text-sm text-gray-500">
                    {project.pages_count} pages
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectsPage;