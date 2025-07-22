import axios from 'axios';

const EMAIL_SERVICE_BASE_URL = 'http://localhost:8000/email-verification';

export interface SendVerificationRequest {
  email: string;
  firstName: string;
  userId: number;
}

export interface VerifyCodeRequest {
  userId: number;
  code: string;
}

export interface VerifyTokenRequest {
  token: string;
}

export interface VerificationResponse {
  success: boolean;
  message: string;
  expiresIn?: number;
  cooldownMs?: number;
  retryAfter?: number;
  userId?: number;
}

export interface VerificationStatusResponse {
  success: boolean;
  verified: boolean;
}

class EmailVerificationService {
  private baseURL: string;

  constructor(baseURL: string = EMAIL_SERVICE_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Enviar e-mail de verificação
   */
  async sendVerificationEmail(data: SendVerificationRequest): Promise<VerificationResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/send-verification`, data);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw error.response.data;
      }
      throw {
        success: false,
        message: 'Erro de conexão com o serviço de e-mail'
      };
    }
  }

  /**
   * Verificar código de 6 dígitos
   */
  async verifyCode(data: VerifyCodeRequest): Promise<VerificationResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/verify-code`, data);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw error.response.data;
      }
      throw {
        success: false,
        message: 'Erro de conexão com o serviço de e-mail'
      };
    }
  }

  /**
   * Verificar token do link do e-mail
   */
  async verifyToken(data: VerifyTokenRequest): Promise<VerificationResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/verify-token`, data);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw error.response.data;
      }
      throw {
        success: false,
        message: 'Erro de conexão com o serviço de e-mail'
      };
    }
  }

  /**
   * Verificar status de verificação do usuário
   */
  async getVerificationStatus(userId: number): Promise<VerificationStatusResponse> {
    try {
      const response = await axios.get(`${this.baseURL}/verification-status/${userId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw error.response.data;
      }
      throw {
        success: false,
        verified: false
      };
    }
  }

  /**
   * Testar conectividade do serviço
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    try {
      const response = await axios.get(`${this.baseURL}/health`);
      return response.data;
    } catch (error: any) {
      throw {
        status: 'ERROR',
        service: 'Email Service',
        timestamp: new Date().toISOString(),
        error: error.message
      };
    }
  }

  /**
   * Enviar e-mail de teste
   */
  async sendTestEmail(): Promise<VerificationResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/test-email`);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw error.response.data;
      }
      throw {
        success: false,
        message: 'Erro ao enviar e-mail de teste'
      };
    }
  }
}

// Instância singleton do serviço
export const emailVerificationService = new EmailVerificationService();

export default EmailVerificationService;
