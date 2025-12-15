"use client";

import React, { useState } from "react";

interface FeedbackFormData {
  feedback_type: string;
  category: string;
  title: string;
  content: string;
  neighborhood: string;
  anonymous: boolean;
  contact_email: string;
}

export default function FeedbackForm() {
  const [formData, setFormData] = useState<FeedbackFormData>({
    feedback_type: "general",
    category: "other",
    title: "",
    content: "",
    neighborhood: "",
    anonymous: true,
    contact_email: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const feedbackTypes = [
    { value: "survey", label: "Survey Response" },
    { value: "complaint", label: "Complaint" },
    { value: "praise", label: "Praise" },
    { value: "suggestion", label: "Suggestion" },
    { value: "question", label: "Question" },
    { value: "concern", label: "Concern" },
    { value: "request", label: "Request" },
    { value: "general", label: "General Feedback" },
  ];

  const categories = [
    { value: "response_time", label: "Response Time" },
    { value: "officer_conduct", label: "Officer Conduct" },
    { value: "community_programs", label: "Community Programs" },
    { value: "safety_concerns", label: "Safety Concerns" },
    { value: "traffic", label: "Traffic" },
    { value: "noise", label: "Noise" },
    { value: "property_crime", label: "Property Crime" },
    { value: "youth_services", label: "Youth Services" },
    { value: "communication", label: "Communication" },
    { value: "accessibility", label: "Accessibility" },
    { value: "other", label: "Other" },
  ];

  const neighborhoods = [
    "Downtown Riviera Beach",
    "Singer Island",
    "West Riviera Beach",
    "Port of Palm Beach Area",
    "Riviera Beach Heights",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    await new Promise((resolve) => setTimeout(resolve, 1000));

    setSubmitted(true);
    setSubmitting(false);
  };

  const handleReset = () => {
    setFormData({
      feedback_type: "general",
      category: "other",
      title: "",
      content: "",
      neighborhood: "",
      anonymous: true,
      contact_email: "",
    });
    setSubmitted(false);
  };

  if (submitted) {
    return (
      <div className="bg-white rounded-lg border p-6">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Thank You for Your Feedback!
          </h3>
          <p className="text-gray-600 mb-4">
            Your feedback has been submitted and will be reviewed by our team.
          </p>
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-blue-900 text-white rounded-lg hover:bg-blue-800"
          >
            Submit Another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Submit Feedback</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Feedback Type
            </label>
            <select
              value={formData.feedback_type}
              onChange={(e) => setFormData({ ...formData, feedback_type: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              {feedbackTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Brief summary of your feedback"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Your Feedback
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            placeholder="Please share your thoughts, concerns, or suggestions..."
            rows={4}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Neighborhood (Optional)
          </label>
          <select
            value={formData.neighborhood}
            onChange={(e) => setFormData({ ...formData, neighborhood: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Select a neighborhood</option>
            {neighborhoods.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="anonymous"
            checked={formData.anonymous}
            onChange={(e) => setFormData({ ...formData, anonymous: e.target.checked })}
            className="mr-2"
          />
          <label htmlFor="anonymous" className="text-sm text-gray-700">
            Submit anonymously
          </label>
        </div>

        {!formData.anonymous && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email (for follow-up)
            </label>
            <input
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
              placeholder="your@email.com"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-2 bg-blue-900 text-white rounded-lg hover:bg-blue-800 disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "Submit Feedback"}
        </button>
      </form>
    </div>
  );
}
