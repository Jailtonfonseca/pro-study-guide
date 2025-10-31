# Usar uma imagem base oficial do Nginx
FROM nginx:alpine

# Copiar o arquivo de configuração personalizado do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar os arquivos estáticos da aplicação (HTML, CSS, JS)
COPY index.html /usr/share/nginx/html/

# Expor a porta 80
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
