import IndustriesView from '@/components/IndustriesView';
import PerEuro from '@/components/PerEuro';
import IoNetwork from '@/components/IoNetwork';
import ExamplePlatform from '@/components/ExamplePlatform';
import { readData } from '@/lib/server';
import type { Headline } from '@/lib/types';

export const metadata = { title: 'Industries' };

export default function Page() {
  const headline = readData<Headline>('cy/headline.json');
  const ex = readData<{ summary: Parameters<typeof ExamplePlatform>[0]['s'] }>('cy/example_platform.json');
  return (
    <>
      <IndustriesView headline={headline} />
      <PerEuro years={headline.io_years} />
      <ExamplePlatform s={ex.summary} />
      <IoNetwork years={headline.io_years} />
    </>
  );
}
