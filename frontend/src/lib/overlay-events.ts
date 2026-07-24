import { useEffect } from "react";

/** Coordinates mutually-exclusive floating overlays (mobile nav sheet, chat widget) that live outside each other's React tree. */
export type OverlayId = "nav" | "chat";

const OVERLAY_OPENED_EVENT = "radcrew:overlay-opened";

export function announceOverlayOpened(id: OverlayId) {
  window.dispatchEvent(new CustomEvent<OverlayId>(OVERLAY_OPENED_EVENT, { detail: id }));
}

/** Closes this overlay whenever a different one announces that it opened. */
export function useCloseOnOtherOverlayOpen(id: OverlayId, close: () => void) {
  useEffect(() => {
    const handler = (event: Event) => {
      const opened = (event as CustomEvent<OverlayId>).detail;
      if (opened !== id) close();
    };
    window.addEventListener(OVERLAY_OPENED_EVENT, handler);
    return () => window.removeEventListener(OVERLAY_OPENED_EVENT, handler);
  }, [id, close]);
}
