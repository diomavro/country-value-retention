import CompareView, { type CompareData } from '@/components/CompareView';
import { readData } from '@/lib/server';

export const metadata = { title: 'Compare countries' };

export default function Page() {
  return <CompareView data={readData<CompareData>('compare.json')} />;
}
