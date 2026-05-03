# SGFH - Sistema de Gestão de Filas

Um sistema web leve e responsivo para orquestração de fluxo de atendimento. Desenvolvido com foco em alta disponibilidade e coleta de métricas de tempo de espera.

## Visão Geral
O SGFH resolve o problema de desorganização em filas de espera físicas. O sistema foi arquitetado em módulos distintos para garantir a melhor experiência de usuário:
- **Totem de Autoatendimento:** Interface rápida para o cliente gerar senhas (Normal ou Prioritária).
- **Painel do Atendente (Guichê):** Área restrita com autenticação para controle de chamadas, respeitando automaticamente a regra de negócios de prioridades.
- **Display de TV:** Painel de visualização em tempo real das chamadas atuais e histórico recente.

O banco de dados captura métricas fundamentais como `criado_em` e `chamado_em`, preparando a infraestrutura de dados para futuras análises de inteligência de negócios e medição de SLAs de atendimento.

## Tecnologias Utilizadas
- **Back-end:** Python 3, Flask
- **Banco de Dados:** SQLite3 (Persistência leve e portátil)
- **Front-end:** HTML5, CSS3, Bootstrap 5

## Como executar o projeto localmente

O sistema foi desenhado para ser portátil e roda perfeitamente em ambientes Linux e Windows.

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/SGFH.git](https://github.com/SEU_USUARIO/SGFH.git)
cd SGFH
