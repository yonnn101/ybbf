/**
 * Parse program in_scope / out_scope from the UI:
 * - Valid JSON object or array (e.g. `["a.com"]` or `{"domains":[]}`) is parsed as-is.
 * - Otherwise treated as a list of domains: split on newlines, commas, or semicolons.
 */
export function parseScopeInput(raw: string): unknown {
  const t = raw.trim();
  if (!t) return [];

  const first = t[0];
  if (first === "{" || first === "[") {
    try {
      return JSON.parse(t) as unknown;
    } catch {
      throw new Error(
        "Invalid JSON. Fix the JSON or use a simple domain list (one per line or comma-separated).",
      );
    }
  }

  const parts = t
    .split(/[\n,;]+/)
    .map((s) => s.trim())
    .filter(Boolean);
  return parts;
}
