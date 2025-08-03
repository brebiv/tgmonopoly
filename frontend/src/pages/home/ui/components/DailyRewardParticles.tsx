import { Application, useApplication, useExtend, useTick } from "@pixi/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Assets, Sprite, Container, Texture } from "pixi.js";

import coin from "@/assets/coin.png";
import { getRandomArbitrary } from "@/shared/utils";

const CoinSprite = ({
  x,
  y,
  // @ts-ignore
  direction,
  speed,
  scale,
}: {
  x: number;
  y: number;
  direction: number;
  speed: number;
  scale: number;
}) => {
  useExtend({ Sprite });
  const spriteRef = useRef(null);
  const { app } = useApplication();
  const [texture, setTexture] = useState(Texture.EMPTY);
  const [position, setPosition] = useState({ x: x, y: y });
  const [alpha, setAlpha] = useState(0.85);
  const updatePosition = useCallback(() => {
    setPosition((prev) => {
      //   let newPos = { x: prev.x + Math.sin(direction) * speed, y: prev.y + Math.cos(direction) * speed };
      let newPos = { x: prev.x, y: prev.y + 1 * speed };

      if (newPos.x > app.screen.width + 10 || newPos.y > app.screen.height + 10) {
        newPos = { x: x, y: y };
        setAlpha(0.85);
        return newPos;
      } else if (newPos.x > 0 && newPos.y > 0) {
        setAlpha((prev) => prev - 0.01 * speed);
      }

      return newPos;
    });
  }, []);

  const propagateThoughPath = () => {
    if (Math.random() > 0.5) {
      setPosition((prev) => ({ x: prev.x, y: Math.random() * (app.screen.height * 0.6) }));
    }
  };

  useEffect(() => {
    if (texture === Texture.EMPTY) {
      Assets.load(coin).then((result) => {
        setTexture(result);
      });
    }
  }, [texture]);

  useEffect(() => {
    propagateThoughPath();
  }, []);

  useTick(updatePosition);

  return (
    <pixiSprite
      ref={spriteRef}
      eventMode={"static"}
      anchor={0.5}
      width={32 * scale}
      height={32 * scale}
      texture={texture}
      x={position.x}
      y={position.y}
      alpha={alpha}
    />
  );
};

type Point = {
  x: number;
  y: number;
};

type ParticleProps = {
  x: number;
  y: number;
  direction: number;
  speed: number;
  scale: number;
} & Point;

const Particles = () => {
  useExtend({ Container });
  const [points, setPoints] = useState<ParticleProps[]>([]);
  const { app } = useApplication();

  useEffect(() => {
    const newPoints = Array.from({ length: 30 }).map(() => ({
      x: Math.random() * app.screen.width,
      y: Math.random() * -app.screen.height,
      direction: Math.random() * Math.PI * 2,
      speed: getRandomArbitrary(0.2, 0.5),
      scale: getRandomArbitrary(0.8, 1),
    }));

    setPoints(newPoints);
  }, []);

  return (
    <pixiContainer>
      {points.map((p) => (
        <CoinSprite x={p.x} y={p.y} direction={p.direction} speed={p.speed} scale={p.scale} />
      ))}
    </pixiContainer>
  );
};

export const DailyRewardParticles = () => {
  useExtend({ Container });
  const parentRef = useRef(null);
  const [init, setInit] = useState(false);

  return (
    <div
      ref={parentRef}
      className="absolute top-0 left-0 z-0 h-full w-full overflow-auto overflow-y-hidden rounded-md"
    >
      <Application
        autoStart
        sharedTicker
        resizeTo={parentRef}
        backgroundAlpha={0}
        onInit={() => setInit(true)}
      >
        {init && <Particles />}
      </Application>
    </div>
  );
};
