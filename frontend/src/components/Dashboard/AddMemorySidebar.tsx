import React, { useState } from 'react';
import { useMemoryStore } from '../../store/memoryStore';
import { memoryService } from '../../services/memoryService';
import { MemoryResult } from '../../types';
import { MaterialIcon } from '@/components/common/MaterialIcon';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export const AddMemorySidebar: React.FC = () => {
  const [content, setContent] = useState('');
  const [type, setType] = useState('knowledge');
  const [tags, setTags] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const { addMemory, setError } = useMemoryStore();

  const handleSave = async () => {
    if (!content.trim()) return;

    setIsSaving(true);
    setError(null);

    try {
      const tagsList = tags.split(',').map(t => t.trim()).filter(Boolean);
      const response = await memoryService.save(content, type, tagsList);

      const newMemory: MemoryResult = {
        id: response.id,
        content: content,
        type: type,
        tags: tagsList,
        created_at: response.created_at,
        score: 0,
        metadata: {}
      };

      addMemory(newMemory);

      // Reset form
      setContent('');
      setTags('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save memory';
      setError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="matte-surface rounded-sm border border-border-main sticky top-24">
      <div className="p-4 border-b border-border-main flex justify-between items-center bg-surface-accent rounded-t-sm">
        <h3 className="text-sm font-heading font-bold uppercase tracking-wide text-foreground">Add New Memory</h3>
        <button className="text-muted-foreground hover:text-foreground transition-colors">
          <MaterialIcon icon="close" size="lg" />
        </button>
      </div>
      <div className="p-6 space-y-6">
        <div className="space-y-2">
          <Label className="block text-xs font-bold uppercase tracking-widest text-muted-foreground">Content</Label>
          <Textarea 
            className="debossed-inset w-full bg-bg-main border border-border-main rounded-sm p-3 text-sm text-foreground placeholder:text-muted-foreground/70 focus:border-primary focus:ring-0 font-mono resize-none" 
            placeholder="What would you like to remember?" 
            rows={4}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label className="block text-xs font-bold uppercase tracking-widest text-muted-foreground">Type</Label>
          <Select value={type} onValueChange={setType}>
            <SelectTrigger className="debossed-inset w-full bg-bg-main border border-border-main rounded-sm py-2.5 pl-3 pr-3 text-sm text-foreground focus:border-primary focus:ring-0 appearance-none font-sans h-auto">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-surface-main border-border-main text-foreground">
              <SelectItem value="knowledge">Knowledge</SelectItem>
              <SelectItem value="event">Event</SelectItem>
              <SelectItem value="code_snippet">Code Snippet</SelectItem>
              <SelectItem value="preference">Preference</SelectItem>
              <SelectItem value="context">Context</SelectItem>
              <SelectItem value="summary">Summary</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label className="block text-xs font-bold uppercase tracking-widest text-muted-foreground">Tags</Label>
          <Input 
            className="debossed-inset w-full bg-bg-main border border-border-main rounded-sm p-2.5 text-sm text-foreground placeholder:text-muted-foreground/70 focus:border-primary focus:ring-0 font-mono h-auto" 
            placeholder="ai, python, research" 
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
          />
          <p className="text-[10px] text-muted-foreground font-mono mt-1">Comma separated</p>
        </div>
        <Button 
          className="w-full bg-primary hover:bg-primary-dark text-primary-foreground font-bold py-3 px-4 rounded-sm shadow-md transition-all flex items-center justify-center gap-2 uppercase text-xs tracking-widest mt-2 h-auto"
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <MaterialIcon icon="progress_activity" className="animate-spin" />
          ) : (
            <MaterialIcon icon="save" className="text-base" />
          )}
          Save Memory
        </Button>
      </div>
    </div>
  );
};
