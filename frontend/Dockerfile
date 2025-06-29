FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clean install with proper cache handling
RUN rm -rf package-lock.json node_modules && \
    npm cache clean --force && \
    npm install --no-optional

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host"]