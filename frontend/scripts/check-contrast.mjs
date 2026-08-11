import { readFileSync } from "node:fs";

const css = readFileSync(
  new URL("../app/styles/globals.css", import.meta.url),
  "utf8",
);
const block = (selector) =>
  css.match(
    new RegExp(`${selector.replace(".", "\\.")}\\s*\\{([^}]+)\\}`),
  )?.[1] ?? "";
const tokens = (body) =>
  Object.fromEntries(
    [...body.matchAll(/--([\w-]+):\s*(#[0-9a-f]{6})/gi)].map((match) => [
      match[1],
      match[2],
    ]),
  );
const light = tokens(block(":root"));
const dark = tokens(block(".dark"));
const luminance = (hex) => {
  const channels = hex
    .slice(1)
    .match(/.{2}/g)
    .map((value) => Number.parseInt(value, 16) / 255)
    .map((value) =>
      value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4,
    );
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
};
const ratio = (foreground, background) => {
  const values = [luminance(foreground), luminance(background)].sort(
    (a, b) => b - a,
  );
  return (values[0] + 0.05) / (values[1] + 0.05);
};
const checks = [
  ["light primary text", light["text-primary"], light.background, 4.5],
  ["light secondary text", light["text-secondary"], light.background, 4.5],
  ["dark primary text", dark["text-primary"], dark.background, 4.5],
  ["dark secondary text", dark["text-secondary"], dark.background, 4.5],
  ...[1, 2, 3, 4].map((index) => [
    `dark chart ${index}`,
    dark[`chart-${index}`],
    dark.background,
    3,
  ]),
];
let failed = false;
for (const [name, foreground, background, threshold] of checks) {
  const result = ratio(foreground, background);
  const pass = result >= threshold;
  console.log(
    `${pass ? "PASS" : "FAIL"} ${name}: ${result.toFixed(2)}:1 (minimum ${threshold}:1)`,
  );
  failed ||= !pass;
}
if (failed) process.exitCode = 1;
