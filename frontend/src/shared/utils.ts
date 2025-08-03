import type { Game } from "@/entities/types";
import classNames, { type Argument } from "classnames";
import { twMerge } from "tailwind-merge";

export const navigateTo = (path: string) => {
  location.assign(path);
};

export const navigateToGame = (game: Game | string) => {
  let gameUUID: string;
  if (typeof game === "string") {
    gameUUID = game;
  } else {
    gameUUID = game.uuid;
  }
  // location.assign(`/game/${gameUUID}`);
  navigateTo(`/game/${gameUUID}`);
};

export const buildGameWebsocketUrl = (gameUUID: string) => {
  const path = "ws/game/" + gameUUID;
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";

  return `${protocol}://${window.location.host}/${path}/?${Telegram.WebApp.initData}`;
};

export const sleep = async (ms: number) => {
  return new Promise((r) => setTimeout(r, ms));
};

export const cn = (...inputs: Argument[]) => {
  return twMerge(classNames(...inputs));
};

// GPT generated code start
interface Point {
  x: number;
  y: number;
}

interface BoundingRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ScatterOptions {
  /** Number of points to generate */
  count: number;
  /** Scale factor for the bounding rectangle (1.0 = original size) */
  scale?: number;
  /** Margin around the scaled rectangle where points can be scattered */
  scatterMargin?: number;
  /** Random seed for reproducible results (optional) */
  seed?: number;
}

/**
 * Generates an array of points scattered around a given bounding rectangle
 * @param boundingRect - The original bounding rectangle
 * @param options - Configuration options for point generation
 * @returns Array of scattered points
 */
function generateScatteredPoints(boundingRect: BoundingRect, options: ScatterOptions): Point[] {
  const { count, scale = 1.0, scatterMargin = 50, seed } = options;

  // Simple seeded random number generator (if seed is provided)
  let randomSeed = seed || Math.random() * 1000000;
  const seededRandom = (): number => {
    randomSeed = (randomSeed * 9301 + 49297) % 233280;
    return randomSeed / 233280;
  };

  const random = seed !== undefined ? seededRandom : Math.random;

  // Scale the bounding rectangle
  const scaledWidth = boundingRect.width * scale;
  const scaledHeight = boundingRect.height * scale;

  // Calculate the center of the original rectangle
  const centerX = boundingRect.x + boundingRect.width / 2;
  const centerY = boundingRect.y + boundingRect.height / 2;

  // Calculate scaled rectangle position (centered on original)
  const scaledRect: BoundingRect = {
    x: centerX - scaledWidth / 2,
    y: centerY - scaledHeight / 2,
    width: scaledWidth,
    height: scaledHeight,
  };

  // Define the scatter area (scaled rect + margin)
  const scatterArea = {
    left: scaledRect.x - scatterMargin,
    right: scaledRect.x + scaledRect.width + scatterMargin,
    top: scaledRect.y - scatterMargin,
    bottom: scaledRect.y + scaledRect.height + scatterMargin,
  };

  const points: Point[] = [];

  for (let i = 0; i < count; i++) {
    let point: Point;
    let attempts = 0;
    const maxAttempts = 100;

    do {
      // Generate random point in scatter area
      point = {
        x: scatterArea.left + random() * (scatterArea.right - scatterArea.left),
        y: scatterArea.top + random() * (scatterArea.bottom - scatterArea.top),
      };
      attempts++;
    } while (
      // Keep generating until point is outside the scaled rectangle
      attempts < maxAttempts &&
      point.x >= scaledRect.x &&
      point.x <= scaledRect.x + scaledRect.width &&
      point.y >= scaledRect.y &&
      point.y <= scaledRect.y + scaledRect.height
    );

    points.push(point);
  }

  return points;
}

/**
 * Helper function to get bounding rectangle from a DOM element
 * @param element - The DOM element
 * @returns BoundingRect object
 */
function getBoundingRectFromElement(element: Element): BoundingRect {
  const rect = element.getBoundingClientRect();
  return {
    x: rect.left,
    y: rect.top,
    width: rect.width,
    height: rect.height,
  };
}

/**
 * Convenience function that works directly with DOM elements
 * @param element - The DOM element to scatter points around
 * @param options - Configuration options for point generation
 * @returns Array of scattered points
 */
function generateScatteredPointsFromElement(element: Element, options: ScatterOptions): Point[] {
  const boundingRect = getBoundingRectFromElement(element);
  return generateScatteredPoints(boundingRect, options);
}

// Example usage:
/*
// Using with a bounding rectangle object
const rect: BoundingRect = { x: 100, y: 100, width: 200, height: 150 };
const points = generateScatteredPoints(rect, {
  count: 20,
  scale: 1.5,
  scatterMargin: 30
});

// Using with a DOM element
const element = document.getElementById('myElement');
if (element) {
  const points = generateScatteredPointsFromElement(element, {
    count: 15,
    scale: 2.0,
    scatterMargin: 40,
    seed: 12345 // for reproducible results
  });
}
*/

export {
  generateScatteredPoints,
  generateScatteredPointsFromElement,
  getBoundingRectFromElement,
  type Point,
  type BoundingRect,
  type ScatterOptions,
};

// GPT generated code end

export const getRandomArbitrary = (min: number, max: number) => {
  return Math.random() * (max - min) + min;
};
