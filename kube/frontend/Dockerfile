# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static HTML
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]
