'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function useAuthPage() {
  const pathname = usePathname();
  return pathname?.startsWith('/auth');
}