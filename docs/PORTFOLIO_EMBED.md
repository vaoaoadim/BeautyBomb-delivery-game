# BeautyBomb Delivery — portfolio iframe contract

This independent concept can be opened in a portfolio popup through an iframe. The portfolio owns the popup and removes the iframe when the visitor closes it; the game does not access the portfolio DOM.

## Game URL and build configuration

Open the deployed game with `?embed=portfolio` and build the game with the exact origin of the future portfolio site:

```text
VITE_PORTFOLIO_PARENT_ORIGIN=https://portfolio.example.com
```

The value must be an origin, not a path, and must not use `*`. Without it, the game remains safe but the close message is intentionally not sent.

## Recommended popup content

```html
<iframe
  src="https://GAME-ORIGIN.example/?embed=portfolio"
  title="BeautyBomb Delivery — интерактивный игровой концепт"
  allow="autoplay; clipboard-write"
  referrerpolicy="strict-origin-when-cross-origin"
  sandbox="allow-scripts allow-same-origin"
></iframe>
```

Size the iframe to its available popup space. On desktop, keep the complete portrait game within the viewport with at least `12px` outer clearance. On mobile, use almost the full available width while retaining a small outer inset. The embedded game draws its own compact frame; the host should not add a second decorative frame.

Do not add a dimmed overlay or any fullscreen background for this concept. The popup should contain only the framed game surface.

## Close-event contract

The red cross in the game sends this event exactly once per active iframe:

```ts
{
  source: "beautybomb-delivery",
  version: 1,
  type: "request-close",
}
```

The host must validate the iframe window, the game origin, and the complete payload before closing:

```ts
window.addEventListener("message", (event) => {
  if (event.origin !== "https://GAME-ORIGIN.example") return;
  if (event.source !== gameIframe.contentWindow) return;

  const message = event.data;
  if (
    message?.source !== "beautybomb-delivery" ||
    message?.version !== 1 ||
    message?.type !== "request-close"
  ) {
    return;
  }

  closeGamePopup();
  gameIframe.remove();
});
```

Removing the iframe is required: it stops Phaser, animation timers, input listeners, and audio. If a host keeps the iframe mounted while visually hiding it, it may suspend and restore the game with these validated messages:

```ts
{ source: "portfolio-host", version: 1, type: "set-game-active", active: false }
{ source: "portfolio-host", version: 1, type: "set-game-active", active: true }
```

The game pauses both its runtime loop and gameplay music when its document becomes hidden or it receives `active: false`, then restores only valid active gameplay when visible again. Standalone launches do not send a close request and continue to work normally.
