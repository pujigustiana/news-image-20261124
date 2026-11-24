// News-24 entrypoint: copies the pre-rendered entry.png from this
// repository into the output directory make.fun grades.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const repoDir = dirname(fileURLToPath(import.meta.url));

mkdirSync(outDir, { recursive: true });
copyFileSync(join(repoDir, "entry.png"), join(outDir, "entry.png"));
