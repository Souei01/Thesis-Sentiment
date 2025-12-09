'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Spinner } from '@/components/ui/spinner';
import Image from 'next/image';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const validateEmail = (email: string): string | null => {
    if (!email) return 'Email is required';
    
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) return 'Invalid email format';
    
    if (!email.endsWith('@wmsu.edu.ph')) {
      return 'Please use your WMSU email address (@wmsu.edu.ph)';
    }
    
    return null;
  };

  const validatePassword = (password: string): string | null => {
    if (!password) return 'Password is required';
    if (password.length < 6) return 'Password must be at least 6 characters';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    
    // Client-side validation
    const emailError = validateEmail(email);
    const passwordError = validatePassword(password);
    
    if (emailError || passwordError) {
      setErrors({
        email: emailError || undefined,
        password: passwordError || undefined,
      });
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(email.toLowerCase().trim(), password);
      
      if (result.success) {
        // Don't wait for navigation, redirect immediately
        router.push('/dashboard');
      } else {
        // Handle backend errors - show clear message for invalid credentials
        if (result.message && (
          result.message.toLowerCase().includes('invalid') ||
          result.message.toLowerCase().includes('incorrect') ||
          result.message.toLowerCase().includes('not found') ||
          result.message.toLowerCase().includes('failed')
        )) {
          setErrors({ general: 'Login failed. Please check your credentials and try again.' });
        } else if (result.errors) {
          const newErrors: any = {};
          Object.keys(result.errors).forEach(key => {
            if (Array.isArray(result.errors[key])) {
              newErrors[key] = result.errors[key][0];
            }
          });
          // If there are field-specific errors, show them; otherwise show general message
          if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
          } else {
            setErrors({ general: 'Login failed. Please check your credentials and try again.' });
          }
        } else {
          setErrors({ general: result.message || 'Login failed. Please check your credentials and try again.' });
        }
      }
    } catch (error) {
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#8E1B1B] text-white flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center p-2">
            <Image 
              src="/wmsulogo.png" 
              alt="WMSU Logo" 
              width={56} 
              height={56}
              className="object-contain"
            />
          </div>
          <h1 className="text-2xl font-bold">Code Sentiment</h1>
        </div>

        <div className="space-y-6">
          <h2 className="text-7xl font-bold leading-tight">
            Understand what Students need <br /> and what they feel
          </h2>
          <p className="text-xl text-white/90 leading-relaxed">
            Using AI-Powered Sentiment Analysis to gain clear, <br /> actionable insights from student feedback.
          </p>
        </div>

        <p className="text-sm text-white/70">©Copyright - 2025/2026</p>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex flex-col items-center gap-4 mb-8">
            <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center p-2">
              <Image 
                src="/wmsulogo.png" 
                alt="WMSU Logo" 
                width={56} 
                height={56}
                className="object-contain"
              />
            </div>
            <h1 className="text-2xl font-bold text-[#8E1B1B]">Code Sentiment</h1>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Log in</h2>
            <p className="text-md text-gray-500">
              Please login to continue to your account.
            </p>
          </div>

          {/* General Error Message */}
          {errors.general && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-start">
              <svg className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span>{errors.general}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors({ ...errors, email: undefined });
                }}
                className={`w-full px-4 py-3 border ${
                  errors.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#8E1B1B]'
                } rounded-lg focus:ring-2 focus:border-transparent outline-none transition-all text-gray-900 placeholder-gray-400`}
                placeholder="eh202201090@wmsu.edu.ph"
                disabled={isLoading}
              />
              {errors.email && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors({ ...errors, password: undefined });
                  }}
                  className={`w-full px-4 py-3 pr-12 border ${
                    errors.password ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-[#8E1B1B]'
                  } rounded-lg focus:ring-2 focus:border-transparent outline-none transition-all text-gray-900 placeholder-gray-400`}
                  placeholder="••••••••"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {errors.password}
                </p>
              )}
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 text-[#8E1B1B] focus:ring-[#8E1B1B] border-gray-300 rounded cursor-pointer"
                disabled={isLoading}
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 cursor-pointer select-none">
                Keep me logged in
              </label>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#8E1B1B] text-white py-3 px-4 rounded-lg font-medium hover:bg-[#6B1414] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#8E1B1B] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <Spinner size="sm" className="border-white border-t-transparent" />
                  Signing in...
                </span>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Create Account Link */}
          <p className="mt-6 text-center text-sm text-gray-600">
            Need an account?{' '}
            <span className="text-[#8E1B1B] font-medium cursor-not-allowed opacity-50">
              Create one
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
