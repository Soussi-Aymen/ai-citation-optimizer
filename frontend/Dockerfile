FROM node:20-slim

WORKDIR /app

# 1. Cache apt-get packages for faster builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Install dependencies
COPY package*.json ./
RUN npm install

# 3. Copy code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
