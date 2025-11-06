import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { api } from '../../services/api';

const ORCIDCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Authenticating with ORCID...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');

        if (error) {
          setStatus('error');
          setMessage(`ORCID authentication failed: ${error}`);
          toast.error('ORCID authentication failed');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }

        if (!code || !state) {
          setStatus('error');
          setMessage('Missing authentication parameters');
          toast.error('Invalid authentication response');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }

        // Send code to backend for token exchange
        const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await api.get(`${baseUrl}/api/v1/auth/orcid/callback`, {
          params: { code, state },
        });

        // Store token and user data
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));

        setStatus('success');
        setMessage('Successfully authenticated! Redirecting...');
        toast.success('Welcome! You have been authenticated with ORCID.');

        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } catch (error: any) {
        console.error('ORCID callback error:', error);
        setStatus('error');
        setMessage(
          error.response?.data?.detail || 'Authentication failed. Please try again.'
        );
        toast.error('Authentication failed');
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-12 px-4 shadow-xl sm:rounded-lg sm:px-10 border border-gray-200">
          <div className="flex flex-col items-center">
            {status === 'loading' && (
              <>
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mb-6"></div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  Authenticating with ORCID
                </h2>
                <p className="text-sm text-gray-600 text-center">{message}</p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
                  <svg
                    className="h-10 w-10 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Success!</h2>
                <p className="text-sm text-gray-600 text-center">{message}</p>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
                  <svg
                    className="h-10 w-10 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  Authentication Failed
                </h2>
                <p className="text-sm text-gray-600 text-center mb-4">{message}</p>
                <button
                  onClick={() => navigate('/login')}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Return to Login
                </button>
              </>
            )}
          </div>
        </div>

        {/* ORCID Info */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div className="flex items-center space-x-3">
            <svg
              className="h-8 w-8"
              viewBox="0 0 256 256"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill="#A6CE39"
                d="M256,128c0,70.7-57.3,128-128,128C57.3,256,0,198.7,0,128C0,57.3,57.3,0,128,0C198.7,0,256,57.3,256,128z"
              />
              <g>
                <path
                  fill="#FFFFFF"
                  d="M86.3,186.2H70.9V79.1h15.4v48.4V186.2z"
                />
                <path
                  fill="#FFFFFF"
                  d="M108.9,79.1h41.6c39.6,0,57,28.3,57,53.6c0,27.5-21.5,53.6-56.8,53.6h-41.8V79.1z M124.3,172.4h24.5 c34.9,0,42.9-26.5,42.9-39.7c0-21.5-13.7-39.7-43.7-39.7h-23.7V172.4z"
                />
                <path
                  fill="#FFFFFF"
                  d="M88.7,56.8c0,5.5-4.5,10.1-10.1,10.1c-5.6,0-10.1-4.6-10.1-10.1c0-5.6,4.5-10.1,10.1-10.1 C84.2,46.7,88.7,51.3,88.7,56.8z"
                />
              </g>
            </svg>
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-900">
                Secure authentication with ORCID
              </p>
              <p className="text-xs text-gray-600">
                ORCID provides a persistent digital identifier for researchers
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ORCIDCallback;
