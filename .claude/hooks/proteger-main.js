const { execSync } = require("child_process");

let raw = "";
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    process.exit(0);
  }

  const command = (input.tool_input && input.tool_input.command) || "";
  if (!/\bgit\b/.test(command)) process.exit(0);

  const isCommit = /\bgit\b[^;&|]*\bcommit\b/.test(command);
  const isPush = /\bgit\b[^;&|]*\bpush\b/.test(command);
  if (!isCommit && !isPush) process.exit(0);

  const pushesToMain = isPush && /\bpush\b[^;&|]*(\s|:)main(\s|$|;|&|\|)/.test(command);

  let branch = "";
  for (const dir of [input.cwd, process.env.CLAUDE_PROJECT_DIR, process.cwd()]) {
    if (!dir) continue;
    try {
      branch = execSync("git rev-parse --abbrev-ref HEAD", {
        cwd: dir,
        stdio: ["ignore", "pipe", "ignore"],
      })
        .toString()
        .trim();
      break;
    } catch {
      branch = "";
    }
  }

  if (branch === "main" || pushesToMain) {
    const action = isCommit ? "commit" : "push";
    process.stderr.write(
      `Bloqueado: no se hace ${action} directo a main. Crea una rama (git switch -c feature/<descripcion>) y abre un PR a main.\n`
    );
    process.exit(2);
  }

  process.exit(0);
});
