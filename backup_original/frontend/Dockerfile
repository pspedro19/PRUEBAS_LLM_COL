FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy all source code (this will be overridden by volume in development)
COPY . .

# Create .next directory to prevent errors
RUN mkdir -p .next

ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://backend:8000

# Expose port
EXPOSE 3000

# Start Next.js in development mode for hot reload
CMD ["npm", "run", "dev", "--", "-p", "3000", "-H", "0.0.0.0"] 