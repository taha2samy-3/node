import { Shield, Code, Server, Lock, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface RuntimeIconProps {
  icon: string;
  className?: string;
}

export default function RuntimeIcon({ icon, className }: RuntimeIconProps) {
  const [hasError, setHasError] = useState(false);
  const isUrl = (icon.startsWith('http://') || icon.startsWith('https://') || icon.startsWith('data:image/')) && !hasError;

  if (icon === 'openssl' || icon === 'fips') {
    return (
      <div className={`relative inline-flex items-center justify-center ${className || 'w-6 h-6'}`}>
        <ShieldCheck className="w-full h-full text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
        <Lock className="w-1/2 h-1/2 absolute text-white dark:text-slate-900" />
      </div>
    );
  }

  if (isUrl) {
    return (
      <img
        src={icon}
        alt="Runtime Icon"
        className={className}
        referrerPolicy="no-referrer"
        onError={() => setHasError(true)}
      />
    );
  }

  switch (icon) {
    case 'shield':
      return <Shield className={className} />;
    case 'dev':
      return <Code className={className} />;
    case 'prod':
      return <Server className={className} />;
    case 'lock':
      return <Lock className={className} />;
    default:
      return <ShieldCheck className={className} />;
  }
}
