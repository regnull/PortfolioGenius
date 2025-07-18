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
    <div>
      <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-sm">
        {displayContent}
      </ReactMarkdown>
      {shouldTruncate && !expanded && (
        <button onClick={() => setExpanded(true)} className="text-blue-600 mt-2 text-sm">
          Show more
        </button>
      )}
    </div>
  );
}
