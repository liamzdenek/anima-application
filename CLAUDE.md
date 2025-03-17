# CardFable Project Guide

## Project Overview
See [PROJECT.md](./PROJECT.md)

## Code Style
- TypeScript with strict mode
- React functional components with hooks
- CSS Modules for styling (.module.css)
- State management with Effector (store/event/effect pattern)
- Directory organization by feature
- Error handling with try/catch and proper logging

## Conventions
- Component files: PascalCase.tsx with matching .module.css
- Utility functions: camelCase.ts
- File imports: Group by external → internal → relative
- Effects/stores: Defined in effectors.ts files