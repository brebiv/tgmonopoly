import 'vite/modulepreload-polyfill';

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../index.css'

import CreateGame from '../components/create_game/CreateGame';

createRoot(document.getElementById('create-game')!).render(
  <StrictMode>
    <CreateGame />
  </StrictMode>,
)
