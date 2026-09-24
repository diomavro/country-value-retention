import FlowsView from '@/components/FlowsView';
import { readData } from '@/lib/server';
import type { Headline } from '@/lib/types';

export const metadata = { title: 'Flows' };

export default function Page() {
  return <FlowsView headline={readData<Headline>('cy/headline.json')} />;
}
