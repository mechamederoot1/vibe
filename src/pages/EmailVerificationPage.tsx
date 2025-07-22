import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, Mail, Clock, RefreshCw, Edit3, ArrowLeft } from 'lucide-react';
import axios from 'axios';

interface VerificationResponse {
  success: boolean;
  message: string;
  expiresIn?: number;
  cooldownMs?: number;
  retryAfter?: number;
}

const EmailVerificationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [verificationCode, setVerificationCode] = useState(['', '', '', '', '', '']);
  const [email, setEmail] = useState('');
  const [editingEmail, setEditingEmail] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');
  const [countdown, setCountdown] = useState(0);
  const [canResend, setCanResend] = useState(true);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Dados do usuário (normalmente viriam do contexto/localStorage)
  const [userData, setUserData] = useState({
    id: null,
    firstName: '',
    lastName: ''
  });

  useEffect(() => {
    // Verificar se há token na URL (verificação automática via link do e-mail)
    const token = searchParams.get('token');
    if (token) {
      verifyWithToken(token);
    }

    // Recuperar dados do usuário do localStorage
    const storedUser = localStorage.getItem('user');
    const pendingUser = localStorage.getItem('pendingVerificationUser');
    const storedEmail = localStorage.getItem('pendingVerificationEmail');

    if (pendingUser) {
      // Usuário recém-registrado
      const user = JSON.parse(pendingUser);
      setUserData(user);
      setEmail(user.email || storedEmail || '');
      setNewEmail(user.email || storedEmail || '');
    } else if (storedUser) {
      // Usuário logado
      const user = JSON.parse(storedUser);
      setUserData(user);
      setEmail(user.email || storedEmail || '');
      setNewEmail(user.email || storedEmail || '');
    }
  }, [searchParams]);

  useEffect(() => {
    // Gerenciar countdown para reenvio
    let interval: NodeJS.Timeout;
    if (countdown > 0) {
      setCanResend(false);
      interval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [countdown]);

  const verifyWithToken = async (token: string) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:3001/verify-token', { token });
      
      if (response.data.success) {
        setIsVerified(true);
        setMessage('E-mail verificado com sucesso! Redirecionando...');
        setMessageType('success');
        
        // Atualizar localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        user.is_verified = true;
        localStorage.setItem('user', JSON.stringify(user));
        
        // Redirecionar após 2 segundos
        setTimeout(() => {
          navigate('/');
        }, 2000);
      }
    } catch (error: any) {
      setMessage(error.response?.data?.message || 'Erro ao verificar token');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (index: number, value: string) => {
    if (value.length > 1) return; // Apenas um dígito por campo
    
    const newCode = [...verificationCode];
    newCode[index] = value;
    setVerificationCode(newCode);

    // Auto-focus próximo campo
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Verificar automaticamente quando todos os campos estiverem preenchidos
    if (newCode.every(digit => digit !== '') && newCode.join('').length === 6) {
      verifyCode(newCode.join(''));
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !verificationCode[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const verifyCode = async (code?: string) => {
    const codeToVerify = code || verificationCode.join('');

    if (codeToVerify.length !== 6) {
      setMessage('Por favor, insira o código completo de 6 dígitos');
      setMessageType('error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:3001/verify-code', {
        userId: userData.id,
        code: codeToVerify
      });

      if (response.data.success) {
        setIsVerified(true);
        setMessage('E-mail verificado com sucesso! Redirecionando...');
        setMessageType('success');

        // Limpar dados temporários e fazer login automático
        const pendingUser = localStorage.getItem('pendingVerificationUser');
        if (pendingUser) {
          const user = JSON.parse(pendingUser);
          localStorage.removeItem('pendingVerificationUser');
          localStorage.removeItem('pendingVerificationEmail');

          // Redirecionar para home - usuário será automaticamente logado pela resposta do backend
          setTimeout(() => {
            window.location.href = '/';
          }, 2000);
        } else {
          // Atualizar dados do usuário existente
          const user = JSON.parse(localStorage.getItem('user') || '{}');
          user.is_verified = true;
          localStorage.setItem('user', JSON.stringify(user));

          // Redirecionar após 2 segundos
          setTimeout(() => {
            navigate('/');
          }, 2000);
        }
      }
    } catch (error: any) {
      setMessage(error.response?.data?.message || 'Código inválido ou expirado');
      setMessageType('error');
      // Limpar código em caso de erro
      setVerificationCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const resendCode = async () => {
    if (!canResend || resendLoading) return;

    setResendLoading(true);
    try {
      const response = await axios.post('http://localhost:3001/send-verification', {
        email: editingEmail ? newEmail : email,
        firstName: userData.firstName,
        userId: userData.id
      });

      if (response.data.success) {
        setMessage('Novo código enviado com sucesso!');
        setMessageType('success');
        setCountdown(Math.ceil(response.data.cooldownMs / 1000));
        
        // Se estava editando e-mail, confirmar a mudança
        if (editingEmail) {
          setEmail(newEmail);
          setEditingEmail(false);
          localStorage.setItem('pendingVerificationEmail', newEmail);
        }
      }
    } catch (error: any) {
      setMessage(error.response?.data?.message || 'Erro ao reenviar código');
      setMessageType('error');
      
      if (error.response?.data?.retryAfter) {
        setCountdown(Math.ceil(error.response.data.retryAfter / 1000));
      }
    } finally {
      setResendLoading(false);
    }
  };

  const updateEmail = () => {
    if (!newEmail || newEmail === email) {
      setEditingEmail(false);
      return;
    }

    // Validar e-mail
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newEmail)) {
      setMessage('Por favor, insira um e-mail válido');
      setMessageType('error');
      return;
    }

    resendCode(); // Enviará para o novo e-mail
  };

  if (isVerified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-800 mb-2">E-mail Verificado!</h1>
          <p className="text-gray-600 mb-4">Seu e-mail foi confirmado com sucesso.</p>
          <div className="flex items-center justify-center space-x-1 text-sm text-gray-500">
            <span>Redirecionando</span>
            <div className="flex space-x-1">
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse"></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Confirme seu E-mail</h1>
          <p className="text-gray-600">
            Enviamos um código de verificação para
          </p>
        </div>

        {/* E-mail Section */}
        <div className="mb-6">
          {editingEmail ? (
            <div className="space-y-3">
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Novo e-mail"
              />
              <div className="flex space-x-2">
                <button
                  onClick={updateEmail}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Confirmar
                </button>
                <button
                  onClick={() => {
                    setEditingEmail(false);
                    setNewEmail(email);
                  }}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
              <span className="text-gray-800 font-medium">{email}</span>
              <button
                onClick={() => setEditingEmail(true)}
                className="text-blue-600 hover:text-blue-700 p-1"
                title="Editar e-mail"
              >
                <Edit3 className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Verification Code */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Código de Verificação
          </label>
          <div className="flex space-x-2 justify-center">
            {verificationCode.map((digit, index) => (
              <input
                key={index}
                ref={(el) => inputRefs.current[index] = el}
                type="text"
                value={digit}
                onChange={(e) => handleCodeChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className="w-12 h-12 text-center text-xl font-bold border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                maxLength={1}
                disabled={loading}
              />
            ))}
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${
            messageType === 'success' ? 'bg-green-100 text-green-700' :
            messageType === 'error' ? 'bg-red-100 text-red-700' :
            'bg-blue-100 text-blue-700'
          }`}>
            {message}
          </div>
        )}

        {/* Verify Button */}
        <button
          onClick={() => verifyCode()}
          disabled={loading || verificationCode.some(digit => digit === '')}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors mb-4"
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Verificando...</span>
            </div>
          ) : (
            'Verificar E-mail'
          )}
        </button>

        {/* Resend Section */}
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Não recebeu o código?</p>
          
          {canResend ? (
            <button
              onClick={resendCode}
              disabled={resendLoading}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm disabled:opacity-50"
            >
              {resendLoading ? (
                <span className="flex items-center justify-center space-x-1">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span>Enviando...</span>
                </span>
              ) : (
                'Reenviar código'
              )}
            </button>
          ) : (
            <div className="flex items-center justify-center space-x-1 text-sm text-gray-500">
              <Clock className="w-3 h-3" />
              <span>Reenviar em {countdown}s</span>
            </div>
          )}
        </div>

        {/* Back to Login */}
        <div className="mt-6 pt-4 border-t border-gray-200 text-center">
          <button
            onClick={() => navigate('/auth')}
            className="text-gray-600 hover:text-gray-700 text-sm flex items-center justify-center space-x-1"
          >
            <ArrowLeft className="w-3 h-3" />
            <span>Voltar ao login</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage;
