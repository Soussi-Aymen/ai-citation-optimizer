FROM node:20-slim

WORKDIR /app

# Enable corepack for pinned pnpm version
RUN corepack enable

# 1. Cache apt-get packages for faster builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Install dependencies with pnpm (reproducible lockfile)
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

# 3. Copy code
COPY . .

EXPOSE 5173

CMD ["pnpm", "run", "dev", "--", "--host"]
