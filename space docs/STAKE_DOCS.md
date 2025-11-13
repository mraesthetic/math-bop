# Stake Engine Software Development Kit  
## Frontend SDK Documentation

---

## 1. Overview – Why Use the Frontend SDK?

The **frontend-sdk** is a PixiJS/Svelte–based toolkit used for developing **web slot games in a declarative way**.

It provides:

- A structured way to build games using **PixiJS** for rendering and **Svelte/SvelteKit** for UI & state.
- A **monorepo** setup using **Turborepo** for code sharing between games and packages.
- A **storybook** environment to prototype and test:
  - Book events
  - Emitter events
  - UI components
- Sample slot games (e.g. `/apps/lines`) which consume output from the **math-sdk**.
- A flexible event-driven architecture so you can add custom behaviour and complex features.

The repo is fully customizable and can be tailored to accommodate custom events and game mechanics of any complexity.

---

## 2. Dependencies

Besides basic web skills (HTML, CSS, JavaScript/TypeScript), these are the primary npm dependencies used in the repo:

- **pixijs** – 2D WebGL renderer for the game canvas  
  <https://www.npmjs.com/package/pixi.js>
- **svelte** – UI framework  
  <https://www.npmjs.com/package/svelte>
- **sveltekit** – Application framework for routing/build  
  <https://www.npmjs.com/package/@sveltejs/kit>
- **pixi-svelte** – In-house package combining PixiJS and Svelte in a declarative way  
  <https://www.npmjs.com/package/pixi-svelte>
- **turborepo** – Monorepo build & task runner  
  <https://www.npmjs.com/package/turbo>
- **storybook** – Component/story explorer  
  <https://www.npmjs.com/package/storybook>
- **xstate** – Finite state machine for game flow and betting logic  
  <https://www.npmjs.com/package/xstate>
- **typescript** – Typed JavaScript  
  <https://www.npmjs.com/package/typescript>
- **pnpm** – Package manager  
  <https://www.npmjs.com/package/pnpm>

---

## 3. High-Level Flow

After a request to the **RGS (Remote Game Server)**, the frontend processes the returned book and events.

### 3.1 Flow Chart

This is a simplified flow chart of how a game is processed after the RGS request. (The real implementation is more complex, but follows the same idea.)

![Game flow after RGS request](./flowchart.png)

Key steps:

1. **Request RGS** – client requests a game result book.
2. Receive `bookEvents` from the RGS.
3. `playBookEvents(bookEvents)` processes each `bookEvent` in sequence.
4. Each `bookEvent` is handled via `bookEventHandlerMap`.
5. Handlers broadcast one or more `emitterEvents`.
6. `eventEmitter` broadcasts to subscribed Svelte components.
7. Components react to `emitterEvents` and update UI/animations.

---

## 4. Book / BookEvent / Play Functions

### 4.1 `playBookEvents()`

Defined in `packages/utils-book/src/createPlayBookUtils.ts`.

- Accepts `bookEvents` (array).
- Iterates through them **one-by-one** using an async `sequence()` function.
- For each event, calls `playBookEvent(bookEvent, context)`.
- **Order matters** – events are resolved in array order.  
  Example: a `win` event must come **after** `spin`, so that win animations only happen after the reels spin.

This function is also used in `MODE_<GAME_MODE>/book/random` stories in Storybook.

### 4.2 `playBookEvent()`

- Takes a single `bookEvent` plus context (often the full `bookEvents` array).
- Looks up the corresponding handler in `bookEventHandlerMap` using `bookEvent.type`.
- Invokes the appropriate `bookEventHandler`.
- Also used in `MODE_<GAME_MODE>/bookEvent/<BOOK_EVENT_TYPE>` stories.

### 4.3 `sequence()`

- Async helper that resolves a list of async functions/promises **one after another**.
- Contrasts with `Promise.all()`, which runs everything concurrently.
- Used to guarantee deterministic ordering of game steps.

---

## 5. Book & BookEvent Structure

### 5.1 Book

A **book** is JSON returned from the RGS for each game. It is mostly composed of `events` (bookEvents).

```ts
// base_books.ts - Example of a base game book

{
  id: 1,
  payoutMultiplier: 0.0,
  events: [
    {
      index: 0,
      type: 'reveal',
      board: [
        [{ name: 'L2' }, { name: 'L1' }, { name: 'L4' }, { name: 'H2' }, { name: 'L1' }],
        [{ name: 'H1' }, { name: 'L5' }, { name: 'L2' }, { name: 'H3' }, { name: 'L4' }],
        [{ name: 'L3' }, { name: 'L5' }, { name: 'L3' }, { name: 'H4' }, { name: 'L4' }],
        [{ name: 'H4' }, { name: 'H3' }, { name: 'L4' }, { name: 'L5' }, { name: 'L1' }],
        [{ name: 'H3' }, { name: 'L3' }, { name: 'L3' }, { name: 'H1' }, { name: 'H1' }],
      ],
      paddingPositions: [216, 205, 195, 16, 65],
      gameType: 'basegame',
      anticipation: [0, 0, 0, 0, 0],
    },
    { index: 1, type: 'setTotalWin', amount: 0 },
    { index: 2, type: 'finalWin', amount: 0 },
  ],
  criteria: '0',
  baseGameWins: 0.0,
  freeGameWins: 0.0,
}
# Stake Engine Software Development Kit  
## Frontend SDK Documentation

---

## 1. Overview – Why Use the Frontend SDK?

The **frontend-sdk** is a PixiJS/Svelte–based toolkit used for developing **web slot games in a declarative way**.

It provides:

- A structured way to build games using **PixiJS** for rendering and **Svelte/SvelteKit** for UI & state.
- A **monorepo** setup using **Turborepo** for code sharing between games and packages.
- A **storybook** environment to prototype and test:
  - Book events
  - Emitter events
  - UI components
- Sample slot games (e.g. `/apps/lines`) which consume output from the **math-sdk**.
- A flexible event-driven architecture so you can add custom behaviour and complex features.

The repo is fully customizable and can be tailored to accommodate custom events and game mechanics of any complexity.

---

## 2. Dependencies

Besides basic web skills (HTML, CSS, JavaScript/TypeScript), these are the primary npm dependencies used in the repo:

- **pixijs** – 2D WebGL renderer for the game canvas  
  <https://www.npmjs.com/package/pixi.js>
- **svelte** – UI framework  
  <https://www.npmjs.com/package/svelte>
- **sveltekit** – Application framework for routing/build  
  <https://www.npmjs.com/package/@sveltejs/kit>
- **pixi-svelte** – In-house package combining PixiJS and Svelte in a declarative way  
  <https://www.npmjs.com/package/pixi-svelte>
- **turborepo** – Monorepo build & task runner  
  <https://www.npmjs.com/package/turbo>
- **storybook** – Component/story explorer  
  <https://www.npmjs.com/package/storybook>
- **xstate** – Finite state machine for game flow and betting logic  
  <https://www.npmjs.com/package/xstate>
- **typescript** – Typed JavaScript  
  <https://www.npmjs.com/package/typescript>
- **pnpm** – Package manager  
  <https://www.npmjs.com/package/pnpm>

---

## 3. High-Level Flow

After a request to the **RGS (Remote Game Server)**, the frontend processes the returned book and events.

### 3.1 Flow Chart

This is a simplified flow chart of how a game is processed after the RGS request. (The real implementation is more complex, but follows the same idea.)

![Game flow after RGS request](./flowchart.png)

Key steps:

1. **Request RGS** – client requests a game result book.
2. Receive `bookEvents` from the RGS.
3. `playBookEvents(bookEvents)` processes each `bookEvent` in sequence.
4. Each `bookEvent` is handled via `bookEventHandlerMap`.
5. Handlers broadcast one or more `emitterEvents`.
6. `eventEmitter` broadcasts to subscribed Svelte components.
7. Components react to `emitterEvents` and update UI/animations.

---

## 4. Book / BookEvent / Play Functions

### 4.1 `playBookEvents()`

Defined in `packages/utils-book/src/createPlayBookUtils.ts`.

- Accepts `bookEvents` (array).
- Iterates through them **one-by-one** using an async `sequence()` function.
- For each event, calls `playBookEvent(bookEvent, context)`.
- **Order matters** – events are resolved in array order.  
  Example: a `win` event must come **after** `spin`, so that win animations only happen after the reels spin.

This function is also used in `MODE_<GAME_MODE>/book/random` stories in Storybook.

### 4.2 `playBookEvent()`

- Takes a single `bookEvent` plus context (often the full `bookEvents` array).
- Looks up the corresponding handler in `bookEventHandlerMap` using `bookEvent.type`.
- Invokes the appropriate `bookEventHandler`.
- Also used in `MODE_<GAME_MODE>/bookEvent/<BOOK_EVENT_TYPE>` stories.

### 4.3 `sequence()`

- Async helper that resolves a list of async functions/promises **one after another**.
- Contrasts with `Promise.all()`, which runs everything concurrently.
- Used to guarantee deterministic ordering of game steps.

---

## 5. Book & BookEvent Structure

### 5.1 Book

A **book** is JSON returned from the RGS for each game. It is mostly composed of `events` (bookEvents).

```ts
// base_books.ts - Example of a base game book

{
  id: 1,
  payoutMultiplier: 0.0,
  events: [
    {
      index: 0,
      type: 'reveal',
      board: [
        [{ name: 'L2' }, { name: 'L1' }, { name: 'L4' }, { name: 'H2' }, { name: 'L1' }],
        [{ name: 'H1' }, { name: 'L5' }, { name: 'L2' }, { name: 'H3' }, { name: 'L4' }],
        [{ name: 'L3' }, { name: 'L5' }, { name: 'L3' }, { name: 'H4' }, { name: 'L4' }],
        [{ name: 'H4' }, { name: 'H3' }, { name: 'L4' }, { name: 'L5' }, { name: 'L1' }],
        [{ name: 'H3' }, { name: 'L3' }, { name: 'L3' }, { name: 'H1' }, { name: 'H1' }],
      ],
      paddingPositions: [216, 205, 195, 16, 65],
      gameType: 'basegame',
      anticipation: [0, 0, 0, 0, 0],
    },
    { index: 1, type: 'setTotalWin', amount: 0 },
    { index: 2, type: 'finalWin', amount: 0 },
  ],
  criteria: '0',
  baseGameWins: 0.0,
  freeGameWins: 0.0,
}
```

// base_books.ts - Example of a setTotalWin bookEvent

{ index: 1, type: 'setTotalWin', amount: 0 }

## 5.3 BookEventHandler

A bookEventHandler is:

An async function taking a bookEvent.

Performs operations such as:
Updating state.
Broadcasting emitterEvents.
Triggering animations and UI changes.

### 5.4 `bookEventHandlerMap`

`bookEventHandlerMap` is an object that maps each `bookEvent.type` to a specific handler function.  
Each handler interprets the book event and usually triggers one or more `emitterEvents` that update the UI.

---

#### 📘 Definition

    type BookEventHandlerMap<TBookEvent, TContext> = {
      [Type in TBookEvent['type']]?: (
        bookEvent: Extract<TBookEvent, { type: Type }>,
        context: TContext
      ) => Promise<void> | void;
    };

---

#### 📂 Example — `/apps/lines/src/game/bookEventHandlerMap.ts`

    import { eventEmitter } from './eventEmitter';
    import type { BookEvent, BookEventContext, BookEventOfType } from './typesBookEvent';

    export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
      // Example handler
      updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
        // Show the free-spin counter component
        eventEmitter.broadcast({ type: 'freeSpinCounterShow' });

        // Update values displayed in the counter
        eventEmitter.broadcast({
          type: 'freeSpinCounterUpdate',
          current: bookEvent.amount,
          total: bookEvent.total,
        });
      },

      // ...add additional handlers here
    };

### 5.4 `bookEventHandlerMap`

`bookEventHandlerMap` is an object that maps each `bookEvent.type` to a specific handler function. Each handler interprets the book event and usually triggers one or more `emitterEvents` that update the UI.

---

#### 📘 Definition

    type BookEventHandlerMap<TBookEvent, TContext> = {
      [Type in TBookEvent['type']]?: (
        bookEvent: Extract<TBookEvent, { type: Type }>,
        context: TContext
      ) => Promise<void> | void;
    };

---

#### 📂 Example — `/apps/lines/src/game/bookEventHandlerMap.ts`

    import { eventEmitter } from './eventEmitter';
    import type { BookEvent, BookEventContext, BookEventOfType } from './typesBookEvent';

    export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
      // Example handler
      updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
        // Show the free-spin counter component
        eventEmitter.broadcast({ type: 'freeSpinCounterShow' });

        // Update values displayed in the counter
        eventEmitter.broadcast({
          type: 'freeSpinCounterUpdate',
          current: bookEvent.amount,
          total: bookEvent.total,
        });
      },

      // ...add additional handlers here
    };


---

### 6. EventEmitter & Emitter Events

#### 6.1 `eventEmitter`

`eventEmitter` connects the JavaScript logic layer with Svelte components through an event-driven model. It allows communication between game systems without prop drilling.

Core methods include:

- `eventEmitter.broadcast(event)` – send an event synchronously.  
- `eventEmitter.broadcastAsync(event)` – send an event asynchronously and await completion.  
- `eventEmitter.subscribeOnMount(handlers)` – attach handlers to Svelte component lifecycle.

---

#### 6.2 `emitterEvent`

An `emitterEvent` is a JSON payload broadcast by the `eventEmitter`.  
It defines an action or change that components react to.

Example:

    {
      type: 'freeSpinCounterUpdate',
      current: 5,
      total: 10
    }

Each `bookEvent` often produces multiple `emitterEvents`, enabling multiple components to animate or react in parallel.

---

#### 6.3 Synchronous EmitterEventHandler

Used for immediate UI updates, such as showing or hiding elements or updating counters.

Broadcast:

    eventEmitter.broadcast({
      type: 'freeSpinCounterUpdate',
      current: undefined,
      total: bookEvent.totalFs,
    });

Receiver:

    context.eventEmitter.subscribeOnMount({
      freeSpinCounterShow: () => (show = true),
      freeSpinCounterHide: () => (show = false),
      freeSpinCounterUpdate: (emitterEvent) => {
        if (emitterEvent.current !== undefined) current = emitterEvent.current;
        if (emitterEvent.total !== undefined) total = emitterEvent.total;
      },
    });

---

#### 6.4 Asynchronous EmitterEventHandler

Used when you must **wait** for something (animations, fades, transitions).

Broadcast:

    await eventEmitter.broadcastAsync({
      type: 'freeSpinIntroUpdate',
      totalFreeSpins: bookEvent.totalFs,
    });

Receiver:

    context.eventEmitter.subscribeOnMount({
      freeSpinIntroUpdate: async (emitterEvent) => {
        freeSpinsFromEvent = emitterEvent.totalFreeSpins;
        await waitForResolve((resolve) => (oncomplete = resolve));
      },
    });

---

#### 6.5 `emitterEventHandlerMap`

Each Svelte component defines an `emitterEventHandlerMap` that links event types to handlers.

Example from `FreeSpinCounter.svelte`:

    <script lang="ts" module>
      export type EmitterEventFreeSpinCounter =
        | { type: 'freeSpinCounterShow' }
        | { type: 'freeSpinCounterHide' }
        | { type: 'freeSpinCounterUpdate'; current?: number; total?: number };
    </script>

    <script lang="ts">
      context.eventEmitter.subscribeOnMount({
        freeSpinCounterShow: () => (show = true),
        freeSpinCounterHide: () => (show = false),
        freeSpinCounterUpdate: (emitterEvent) => {
          if (emitterEvent.current !== undefined) current = emitterEvent.current;
          if (emitterEvent.total !== undefined) total = emitterEvent.total;
        },
      });
    </script>

Guideline: Each handler should have a **single responsibility**.  
This ensures code remains clean and modular, following SOLID principles.

---

### 7. Task Breakdown

Task Breakdown is the concept of splitting complex game behaviours into smaller, testable parts.  
Each large `bookEvent` should be broken into multiple atomic `emitterEvents`.

Example — instead of one large `tumbleBoard` event, break it down into:

- `tumbleBoardShow`  
- `tumbleBoardInit`  
- `tumbleBoardExplode`  
- `tumbleBoardRemoveExploded`  
- `tumbleBoardSlideDown`  
- `tumbleBoardReset`  
- `tumbleBoardHide`

Handler Example:

    tumbleBoard: async (bookEvent: BookEventOfType<'tumbleBoard'>) => {
      eventEmitter.broadcast({ type: 'tumbleBoardShow' });
      eventEmitter.broadcast({ type: 'tumbleBoardInit', addingBoard: bookEvent.newSymbols });
      await eventEmitter.broadcastAsync({
        type: 'tumbleBoardExplode',
        explodingPositions: bookEvent.explodingSymbols,
      });
      eventEmitter.broadcast({ type: 'tumbleBoardRemoveExploded' });
      await eventEmitter.broadcastAsync({ type: 'tumbleBoardSlideDown' });
      eventEmitter.broadcast({ type: 'boardSettle', board: stateGameDerived.tumbleBoardCombined() });
      eventEmitter.broadcast({ type: 'tumbleBoardReset' });
      eventEmitter.broadcast({ type: 'tumbleBoardHide' });
    };

Receiver Example:

    context.eventEmitter.subscribeOnMount({
      tumbleBoardShow: () => {},
      tumbleBoardHide: () => {},
      tumbleBoardInit: () => {},
      tumbleBoardReset: () => {},
      tumbleBoardExplode: () => {},
      tumbleBoardRemoveExploded: () => {},
      tumbleBoardSlideDown: () => {},
    });

Breaking logic this way improves readability, testing, and reusability.

---

#### 7.2 Stateless vs Stateful Games

Stateless games – one RGS request plays a full game (e.g. slot spin).  
Stateful games – multiple requests complete a single session (e.g. Mines).

Even stateless games can be complex, but using atomic emitter events keeps structure consistent.  
Each bookEvent is processed as a chain of emitterEvents that multiple components can react to.

---

### 8. Steps to Add a New BookEvent

Example: Adding a `updateGlobalMult` event to `/apps/lines`.

#### 8.1 Add Data

In `bonus_books.ts`:

    {
      type: 'updateGlobalMult',
      globalMult: 3,
    }

In `bonus_events.ts`:

    export default {
      updateGlobalMult: {
        type: 'updateGlobalMult',
        globalMult: 3,
      },
    };

#### 8.2 Add Storybook Story

In `ModeBonusBookEvent.stories.svelte`:

    <Story
      name="updateGlobalMult"
      args={templateArgs({
        skipLoadingScreen: true,
        data: events.updateGlobalMult,
        action: async (data) => await playBookEvent(data, { bookEvents: [] }),
      })}
    />

#### 8.3 Extend Type Definitions

In `typesBookEvent.ts`:

    type BookEventUpdateGlobalMult = {
      index: number;
      type: 'updateGlobalMult';
      globalMult: number;
    };

    export type BookEvent =
      | ExistingBookEventTypes
      | BookEventUpdateGlobalMult;

#### 8.4 Add to Handler Map

In `bookEventHandlerMap.ts`:

    updateGlobalMult: async (bookEvent: BookEventOfType<'updateGlobalMult'>) => {
      eventEmitter.broadcast({ type: 'globalMultiplierShow' });
      eventEmitter.broadcast({
        type: 'globalMultiplierUpdate',
        multiplier: bookEvent.globalMult,
      });
    },

#### 8.5 Create Component

In `GlobalMultiplier.svelte`:

    <script lang="ts" module>
      export type EmitterEventGlobalMultiplier =
        | { type: 'globalMultiplierShow' }
        | { type: 'globalMultiplierHide' }
        | { type: 'globalMultiplierUpdate'; multiplier: number };
    </script>

#### 8.6 Wire EmitterEvent Types

In `typesEmitterEvent.ts`:

    import type { EmitterEventGlobalMultiplier } from '../components/GlobalMultiplier.svelte';
    export type EmitterEventGame = ExistingEvents | EmitterEventGlobalMultiplier;

#### 8.7 Update EventEmitter Type

In `eventEmitter.ts`:

    import type { EmitterEventGame } from './typesEmitterEvent';
    export type EmitterEvent = EmitterEventUi | EmitterEventHotKey | EmitterEventGame;
    export const { eventEmitter } = createEventEmitter<EmitterEvent>();

#### 8.8 Add Logic

In `GlobalMultiplier.svelte`:

    <script lang="ts">
      const context = getContext();
      let show = false;
      let multiplier = 1;

      context.eventEmitter.subscribeOnMount({
        globalMultiplierShow: () => (show = true),
        globalMultiplierHide: () => (show = false),
        globalMultiplierUpdate: async (emitterEvent) => {
          multiplier = emitterEvent.multiplier;
          console.log('Multiplier:', multiplier);
        },
      });
    </script>

---

### 9. File Structure Overview

    root
      |_ apps
      |   |_ cluster
      |   |_ lines
      |   |_ scatter
      |   |_ ways
      |
      |_ packages
          |_ config-*
          |_ constants-*
          |_ state-*
          |_ utils-*
          |_ components-*
          |_ pixi-*

- `/apps` → individual games.  
- `/packages` → shared utilities, constants, state systems, and components.

---

### 10. Context System Recap

Each app initializes context at entry level using `setContext()` to make global states available:

- `ContextEventEmitter` — provides the event emitter.  
- `ContextLayout` — provides layout data and canvas sizing.  
- `ContextXstate` — provides finite state machine state.  
- `ContextApp` — provides PIXI app context and assets.

All components access shared states via `getContext*()` functions.

---

### 11. UI Packages

- `components-ui-pixi` – reusable Pixi-based UI (buttons, HUD, etc.).  
- `components-ui-html` – HTML overlays (modals, version labels, etc.).  

They are functional, but meant as **examples or starting points**.  
You can use them for rapid prototyping or replace them with your own styled UI.

We have re-vamped the UI bottom bar so no need to worry about that.

---
