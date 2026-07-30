import { Shield, Code, Server } from 'lucide-react';

interface RuntimeIconProps {
  icon: string;
  className?: string;
}

export default function RuntimeIcon({ icon, className }: RuntimeIconProps) {
  const isUrl = icon.startsWith('http://') || icon.startsWith('https://') || icon.startsWith('data:image/');

  if (isUrl) {
    return <img src={icon} alt="Runtime Icon" className={className} referrerPolicy="no-referrer" />;
  }

  switch (icon) {
    case 'shield':
      return <Shield className={className} />;
    case 'dev':
      return <Code className={className} />;
    case 'prod':
      return <Server className={className} />;
    default:
      return <Shield className={className} />;
  }
}
