import { Copy, Download, Link2, RotateCcw } from "lucide-react";
import { useNavigate } from "react-router";
import { api } from "../../api";
import { copyText } from "../../lib/clipboard";
import { clearProgress } from "../../lib/plannerState";
import { Button, buttonClass } from "../ButtonLink";

/** Copy, download, share, start over. `notify` shows the toast. */
export function ActionBar({ planId, notify }: { planId: string; notify: (message: string) => void }) {
  const navigate = useNavigate();

  async function copyBrief() {
    try {
      const response = await fetch(api.exportUrl(planId, "md"));
      if (!response.ok) throw new Error(String(response.status));
      notify((await copyText(await response.text())) ? "Copied!" : "Couldn't copy. Use Download .md instead.");
    } catch {
      notify("Couldn't load the brief. Check your connection and try again.");
    }
  }

  async function copyLink() {
    const ok = await copyText(`${window.location.origin}/plan/${planId}`);
    notify(ok ? "Link copied" : "Couldn't copy. Copy the address from your browser bar.");
  }

  function startNew() {
    clearProgress();
    navigate("/planner");
  }

  const secondary = buttonClass("secondary", "md");
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
      <div className="grid grid-cols-3 gap-2 sm:flex sm:flex-wrap">
        <Button onClick={copyBrief} className="col-span-3 sm:col-span-1">
          <Copy className="size-4" aria-hidden="true" />
          Copy brief
        </Button>
        <a href={api.exportUrl(planId, "md")} download className={secondary} aria-label="Download .md">
          <Download className="size-4" aria-hidden="true" />
          <span className="sm:hidden">.md</span>
          <span className="hidden sm:inline">Download .md</span>
        </a>
        <a href={api.exportUrl(planId, "txt")} download className={secondary} aria-label="Download .txt">
          <Download className="size-4" aria-hidden="true" />
          <span className="sm:hidden">.txt</span>
          <span className="hidden sm:inline">Download .txt</span>
        </a>
        <Button variant="secondary" onClick={copyLink} aria-label="Copy share link">
          <Link2 className="size-4" aria-hidden="true" />
          <span className="sm:hidden">Link</span>
          <span className="hidden sm:inline">Copy share link</span>
        </Button>
      </div>
      <button
        type="button"
        onClick={startNew}
        className="inline-flex items-center gap-1.5 self-start rounded-lg px-2 py-2 text-[0.95rem] font-semibold text-violet-deep hover:bg-violet-50 sm:self-auto"
      >
        <RotateCcw className="size-4" aria-hidden="true" />
        Start a new plan
      </button>
    </div>
  );
}
