import type { NextConfig } from "next";
import path from "path";
import { fileURLToPath } from "url";

const apiInternalUrl =
  process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    root: frontendRoot,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiInternalUrl}/api/v1/:path*`,
      },
    ];
  },
  async redirects() {
    return [
      { source: "/riesgo", destination: "/radar", permanent: false },
      { source: "/indicadores", destination: "/radar", permanent: false },
      { source: "/anomalias", destination: "/radar", permanent: false },
      { source: "/tendencias", destination: "/radar", permanent: false },
      { source: "/insights", destination: "/radar", permanent: false },
    ];
  },
};

export default nextConfig;
