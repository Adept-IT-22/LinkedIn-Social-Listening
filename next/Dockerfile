FROM node:20-alpine as base

# DEPENDENCIES STAGE
FROM base as deps 
RUN apk add --no-cache libc6-compat 
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --production=false

#BUILDER STAGE
FROM base as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

#PRODUCTION STAGE
FROM base as production
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME 0.0.0.0

CMD ["node", "server.js"]
