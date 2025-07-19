'use client';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownViewerProps {
  content: string;
  maxLines?: number;
}

export default function MarkdownViewer({ content, maxLines = 4 }: MarkdownViewerProps) {
  const [expanded, setExpanded] = useState(false);

  const lines = content.split('\n');
  const shouldTruncate = lines.length > maxLines;
  const displayContent = expanded || !shouldTruncate ? content : lines.slice(0, maxLines).join('\n');

  return (
    <div className="text-gray-900">
      <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-sm prose-gray max-w-none">
        {displayContent}
      </ReactMarkdown>
      {shouldTruncate && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-blue-600 hover:text-blue-700 mt-2 text-sm font-medium"
        >
          {expanded ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  );
}
