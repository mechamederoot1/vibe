# Acesso Mobile

Este aplicativo agora está configurado para permitir acesso de dispositivos móveis na mesma rede.

## Como Acessar do Mobile

### 1. Endereços Disponíveis

O servidor está rodando nos seguintes endereços:

- **Local**: http://localhost:5173/
- **Rede**: http://172.19.11.66:5173/
- **Rede**: http://172.19.11.67:5173/

### 2. Conectar do Mobile

1. Certifique-se de que seu dispositivo móvel está na mesma rede Wi-Fi
2. Use um dos endereços de rede listados acima no navegador do seu móvel
3. Exemplo: `http://172.19.11.66:5173/`

### 3. Configurações Aplicadas

- Vite configurado com `host: '0.0.0.0'` para permitir conexões externas
- Porta padrão: 5173
- HMR (Hot Module Replacement) configurado para funcionar corretamente
- Preview mode também disponível na porta 4173

### 4. Troubleshooting

- Se não conseguir acessar, verifique se o firewall permite conexões na porta 5173
- Certifique-se de que o dispositivo móvel está na mesma rede
- Tente os diferentes endereços de rede listados pelo Vite

### 5. Comandos Úteis

```bash
# Iniciar servidor dev
npm run dev

# Build do projeto
npm run build

# Preview da build
npm run preview
```

O aplicativo agora está otimizado para desenvolvimento e teste em dispositivos móveis!
