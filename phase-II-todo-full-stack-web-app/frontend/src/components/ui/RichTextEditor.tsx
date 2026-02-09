import React, { useState, useRef, useEffect } from 'react';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({ value, onChange, placeholder, className = '' }) => {
  const [isFocused, setIsFocused] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.innerHTML = value;
    }
  }, [value]);

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
  };

  const formatText = (command: string, value: string = '') => {
    document.execCommand(command, false, value);
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  return (
    <div className={`border rounded-md overflow-hidden ${className}`}>
      {/* Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 p-1 flex flex-wrap gap-1 dark:bg-gray-700 dark:border-gray-600">
        <button
          type="button"
          onClick={() => formatText('bold')}
          className="p-1.5 rounded text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          title="Bold"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          onClick={() => formatText('italic')}
          className="p-1.5 rounded text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          title="Italic"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          onClick={() => formatText('underline')}
          className="p-1.5 rounded text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          title="Underline"
        >
          <u>U</u>
        </button>
        <div className="border-l border-gray-300 mx-1 h-6 self-center dark:border-gray-600"></div>
        <button
          type="button"
          onClick={() => formatText('insertUnorderedList')}
          className="p-1.5 rounded text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          title="Bullet List"
        >
          • List
        </button>
        <button
          type="button"
          onClick={() => formatText('insertOrderedList')}
          className="p-1.5 rounded text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          title="Numbered List"
        >
          1. List
        </button>
      </div>

      {/* Editor */}
      <div
        ref={editorRef}
        contentEditable
        className={`min-h-[120px] p-3 focus:outline-none bg-white dark:bg-gray-800 dark:text-white ${
          isFocused ? 'ring-1 ring-blue-500' : ''
        }`}
        onInput={handleInput}
        onPaste={handlePaste}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        data-placeholder={placeholder}
        suppressContentEditableWarning={true}
        style={{
          position: 'relative'
        }}
      />
    </div>
  );
};

export default RichTextEditor;