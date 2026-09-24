export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || '';
export const dataUrl = (p: string) => `${BASE_PATH}/data/${p}`;
