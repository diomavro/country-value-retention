import Overview from '@/components/Overview';
import { readData } from '@/lib/server';
import type { Headline } from '@/lib/types';

export default function Home() {
  const headline = readData<Headline>('cy/headline.json');
  return <Overview headline={headline} />;
}
