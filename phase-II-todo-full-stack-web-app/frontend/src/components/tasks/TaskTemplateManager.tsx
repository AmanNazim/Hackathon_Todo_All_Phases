'use client';

import React, { useState } from 'react';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

interface TaskTemplate {
  id: string;
  name: string;
  description?: string;
  title: string;
  taskDescription?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags?: string[];
  estimatedDuration?: number; // in minutes
  checklist?: string[];
}

interface TaskTemplateManagerProps {
  templates: TaskTemplate[];
  onCreateTemplate: (template: Omit<TaskTemplate, 'id'>) => Promise<void>;
  onUpdateTemplate: (id: string, template: Partial<TaskTemplate>) => Promise<void>;
  onDeleteTemplate: (id: string) => Promise<void>;
  onUseTemplate: (template: TaskTemplate) => void;
  className?: string;
}

export default function TaskTemplateManager({
  templates,
  onCreateTemplate,
  onUpdateTemplate,
  onDeleteTemplate,
  onUseTemplate,
  className = '',
}: TaskTemplateManagerProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TaskTemplate | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    title: '',
    taskDescription: '',
    priority: 'medium' as TaskTemplate['priority'],
    tags: [] as string[],
    estimatedDuration: 30,
    checklist: [] as string[],
  });

  const [tagInput, setTagInput] = useState('');
  const [checklistInput, setChecklistInput] = useState('');

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      title: '',
      taskDescription: '',
      priority: 'medium',
      tags: [],
      estimatedDuration: 30,
      checklist: [],
    });
    setTagInput('');
    setChecklistInput('');
  };

  const handleCreateTemplate = async () => {
    if (!formData.name || !formData.title) {
      alert('Template name and task title are required');
      return;
    }

    setIsProcessing(true);
    try {
      await onCreateTemplate(formData);
      setIsCreateModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create template:', error);
      alert('Failed to create template');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEditTemplate = async () => {
    if (!selectedTemplate) return;

    setIsProcessing(true);
    try {
      await onUpdateTemplate(selectedTemplate.id, formData);
      setIsEditModalOpen(false);
      setSelectedTemplate(null);
      resetForm();
    } catch (error) {
      console.error('Failed to update template:', error);
      alert('Failed to update template');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    setIsProcessing(true);
    try {
      await onDeleteTemplate(id);
    } catch (error) {
      console.error('Failed to delete template:', error);
      alert('Failed to delete template');
    } finally {
      setIsProcessing(false);
    }
  };

  const openEditModal = (template: TaskTemplate) => {
    setSelectedTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      title: template.title,
      taskDescription: template.taskDescription || '',
      priority: template.priority,
      tags: template.tags || [],
      estimatedDuration: template.estimatedDuration || 30,
      checklist: template.checklist || [],
    });
    setIsEditModalOpen(true);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const removeTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter((t) => t !== tag) });
  };

  const addChecklistItem = () => {
    if (checklistInput.trim()) {
      setFormData({ ...formData, checklist: [...formData.checklist, checklistInput.trim()] });
      setChecklistInput('');
    }
  };

  const removeChecklistItem = (index: number) => {
    setFormData({
      ...formData,
      checklist: formData.checklist.filter((_, i) => i !== index),
    });
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      case 'high':
        return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200';
      case 'medium':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';
    }
  };

  const TemplateForm = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Template Name *
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="e.g., Weekly Report"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Template Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          rows={2}
          placeholder="What is this template for?"
        />
      </div>

      <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Task Details
        </h4>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Task Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder="Task title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Task Description
            </label>
            <textarea
              value={formData.taskDescription}
              onChange={(e) => setFormData({ ...formData, taskDescription: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              rows={3}
              placeholder="Task description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Priority
            </label>
            <select
              value={formData.priority}
              onChange={(e) =>
                setFormData({ ...formData, priority: e.target.value as TaskTemplate['priority'] })
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Estimated Duration (minutes)
            </label>
            <input
              type="number"
              value={formData.estimatedDuration}
              onChange={(e) =>
                setFormData({ ...formData, estimatedDuration: parseInt(e.target.value) || 0 })
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Add tag"
              />
              <Button onClick={addTag} variant="secondary" size="sm">
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                >
                  {tag}
                  <button
                    onClick={() => removeTag(tag)}
                    className="hover:text-blue-600 dark:hover:text-blue-300"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Checklist Items
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={checklistInput}
                onChange={(e) => setChecklistInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addChecklistItem())}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Add checklist item"
              />
              <Button onClick={addChecklistItem} variant="secondary" size="sm">
                Add
              </Button>
            </div>
            <div className="space-y-1">
              {formData.checklist.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded"
                >
                  <span className="flex-1 text-sm text-gray-900 dark:text-white">{item}</span>
                  <button
                    onClick={() => removeChecklistItem(index)}
                    className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg shadow ${className}`}>
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Task Templates</h3>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create Template
          </Button>
        </div>
      </div>

      <div className="p-6">
        {templates.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-600 dark:text-gray-400 mb-4">No templates yet</p>
            <Button onClick={() => setIsCreateModalOpen(true)}>Create your first template</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white">{template.name}</h4>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getPriorityColor(template.priority)}`}>
                    {template.priority}
                  </span>
                </div>

                {template.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {template.description}
                  </p>
                )}

                <div className="text-xs text-gray-500 dark:text-gray-400 mb-3 space-y-1">
                  <p>Task: {template.title}</p>
                  {template.estimatedDuration && (
                    <p>Duration: {template.estimatedDuration} min</p>
                  )}
                  {template.tags && template.tags.length > 0 && (
                    <p>Tags: {template.tags.join(', ')}</p>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => onUseTemplate(template)}
                    variant="primary"
                    size="sm"
                    className="flex-1"
                  >
                    Use Template
                  </Button>
                  <Button
                    onClick={() => openEditModal(template)}
                    variant="secondary"
                    size="sm"
                  >
                    Edit
                  </Button>
                  <Button
                    onClick={() => handleDeleteTemplate(template.id)}
                    variant="danger"
                    size="sm"
                    disabled={isProcessing}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Template Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create Task Template"
      >
        <TemplateForm />
        <div className="flex justify-end gap-3 mt-6">
          <Button
            onClick={() => {
              setIsCreateModalOpen(false);
              resetForm();
            }}
            variant="secondary"
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button onClick={handleCreateTemplate} disabled={isProcessing}>
            {isProcessing ? 'Creating...' : 'Create Template'}
          </Button>
        </div>
      </Modal>

      {/* Edit Template Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedTemplate(null);
          resetForm();
        }}
        title="Edit Task Template"
      >
        <TemplateForm />
        <div className="flex justify-end gap-3 mt-6">
          <Button
            onClick={() => {
              setIsEditModalOpen(false);
              setSelectedTemplate(null);
              resetForm();
            }}
            variant="secondary"
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button onClick={handleEditTemplate} disabled={isProcessing}>
            {isProcessing ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
