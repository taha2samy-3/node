import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { PendingMark } from '../components/Logo';

export default function NotFound({ message = 'This page does not exist.' }: { message?: string }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 px-6 py-24 text-center">
      <PendingMark className="h-20 w-20 text-slate-400 dark:text-slate-600" />
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Not found</h1>
      <p className="text-slate-500 dark:text-slate-400">{message}</p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-700 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
      >
        <ArrowLeft className="h-4 w-4" /> Back to overview
      </Link>
    </div>
  );
}
