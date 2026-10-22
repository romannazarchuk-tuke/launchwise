import { useEffect } from "react";

const SITE = "LaunchWise";

/** Sets document.title for the current page, e.g. useTitle("About") -> "About | LaunchWise". */
export function useTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} | ${SITE}` : `${SITE}: plan your small business website in 3 minutes`;
  }, [title]);
}
