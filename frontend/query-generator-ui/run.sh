#!/bin/sh

npx vite build
npx vite preview --port ${VITE_APP_PORT} --host 0.0.0.0
