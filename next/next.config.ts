import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

/* needed to add support for docker */
module.exports = {
  output: "standalone"
}

export default nextConfig;
