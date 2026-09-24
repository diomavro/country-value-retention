import OwnershipView from '@/components/OwnershipView';
import { readData } from '@/lib/server';
import type { Ownership } from '@/lib/types';

export const metadata = { title: 'Ownership' };

export default function Page() {
  return <OwnershipView o={readData<Ownership>('cy/ownership.json')} />;
}
