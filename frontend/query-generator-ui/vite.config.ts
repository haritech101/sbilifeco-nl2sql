import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const theEnv = loadEnv("", "");

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        allowedHosts: ["all"],
        host: "0.0.0.0",
        port: parseInt(theEnv?.VITE_APP_PORT || "80"),
    },
});
