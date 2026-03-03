import React from 'react';
import { MaterialIcon } from '@/components/common/MaterialIcon';

export const ProTipCard: React.FC = () => {
  return (
    <div className="mt-6 p-4 bg-gradient-to-br from-primary-dark/20 to-bg-main border border-primary/20 rounded-sm relative overflow-hidden">
      <div className="absolute right-0 top-0 opacity-10 text-primary pointer-events-none transform translate-x-1/3 -translate-y-1/3">
        <MaterialIcon icon="psychology" size="2xl" className="text-8xl" />
      </div>
      <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-2 flex items-center gap-2">
        Pro Tip
      </h4>
      <p className="text-xs text-gray-400 leading-relaxed relative z-10">
        You can ask questions in natural language to retrieve related context from multiple memories at once.
      </p>
    </div>
  );
};
