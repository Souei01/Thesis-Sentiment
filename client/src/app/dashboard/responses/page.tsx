'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/DashboardLayout';
import FeedbackResponseTracking from '@/components/FeedbackResponseTracking';

export default function ResponsesPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute allowedRoles={['admin', 'faculty']}>
      <DashboardLayout>
        <FeedbackResponseTracking userRole={user?.role || 'faculty'} />
      </DashboardLayout>
    </ProtectedRoute>
  );
}
