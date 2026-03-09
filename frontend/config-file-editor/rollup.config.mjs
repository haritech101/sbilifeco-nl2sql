import { nodeResolve } from "@rollup/plugin-node-resolve";

export default {
    input: "editor-ui/scripts/home.js",
    output: {
        file: "editor-ui/scripts/home-bundle.js",
        format: "es",
    },
    plugins: [nodeResolve()],
};
