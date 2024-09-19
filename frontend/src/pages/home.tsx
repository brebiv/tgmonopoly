import 'vite/modulepreload-polyfill';

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Home from '../components/home/Home';
import '../index.css'

createRoot(document.getElementById('home')!).render(
  <StrictMode>
    <Home />
  </StrictMode>,
)
