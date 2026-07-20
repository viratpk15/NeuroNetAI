# Production Dockerfile for NeuroNet AI Frontend
FROM node:20-slim as builder

WORKDIR /app

# Install dependencies
COPY package.json ./
COPY package-lock.json* ./
RUN npm ci --omit=dev

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-slim

WORKDIR /app

# Copy package files for production dependencies
COPY package.json ./
COPY package-lock.json* ./
RUN npm ci --omit=dev

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run production server
CMD ["npm", "run", "start"]