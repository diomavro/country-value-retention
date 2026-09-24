import CountryDashboard from '@/components/CountryDashboard';
import { readData } from '@/lib/server';
import type { Headline } from '@/lib/types';

export const metadata = { title: 'Cyprus' };

export default function Page() {
  return <CountryDashboard headline={readData<Headline>('cy/headline.json')} />;
}
