# Use Node.js Alpine image
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose React port
EXPOSE 3000

# 🔥 VERY IMPORTANT ENV (Docker + React fix)
ENV HOST=0.0.0.0
ENV PORT=3000
ENV WDS_SOCKET_PORT=0

# Start React app
CMD ["npm", "start"]


