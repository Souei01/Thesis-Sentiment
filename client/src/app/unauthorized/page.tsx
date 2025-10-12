'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ShieldAlert } from 'lucide-react';

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md px-6">
        <div className="mx-auto w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
          <ShieldAlert className="w-10 h-10 text-red-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Access Denied</h1>
        <p className="text-gray-600 mb-8">
          You don&apos;t have permission to access this page. Only administrators and faculty members can view the dashboard.
        </p>
        <div className="flex gap-4 justify-center">
          <Button
            onClick={() => router.back()}
            variant="outline"
          >
            Go Back
          </Button>
          <Button
            onClick={() => router.push('/login')}
            className="bg-[#8E1B1B] hover:bg-[#6B1414]"
          >
            Return to Login
          </Button>
        </div>
      </div>
    </div>
  );
}
