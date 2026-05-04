const WEB3FORMS_URL = "https://api.web3forms.com/submit";

export function getWeb3FormsAccessKey(): string | undefined {
  const k = import.meta.env.VITE_WEB3FORMS_ACCESS_KEY;
  return typeof k === "string" && k.trim().length > 0 ? k.trim() : undefined;
}

export async function submitWeb3Form(fields: Record<string, string>): Promise<void> {
  const access_key = getWeb3FormsAccessKey();
  if (!access_key) {
    throw new Error("Web3Forms is not configured (missing VITE_WEB3FORMS_ACCESS_KEY).");
  }
  const res = await fetch(WEB3FORMS_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_key, ...fields }),
  });
  const data = (await res.json().catch(() => ({}))) as { success?: boolean; message?: string };
  if (!res.ok || !data.success) {
    throw new Error(typeof data.message === "string" ? data.message : "Form submission failed.");
  }
}
