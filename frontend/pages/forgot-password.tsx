"use client";

import React from 'react';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  return (
    <main className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-lg text-center">
        <h1 className="text-2xl font-bold text-slate-800 mb-4">Password Reset</h1>
        <p className="text-slate-600 mb-6">This feature is under construction. Please check back later.</p>
        <Link href="/login" className="text-sm text-blue-600 hover:underline">
          Back to Login
        </Link>
      </div>
    </main>
  );
}
