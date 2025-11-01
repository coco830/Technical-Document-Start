#!/bin/bash
cd frontend/src

# Fix use-auth.ts
if [ -f hooks/use-auth.ts ]; then
  sed -i "s/import { useState, useEffect, useCallback } from 'react'/import React, { useState, useEffect, useCallback } from 'react'/" hooks/use-auth.ts
  echo "✅ Fixed hooks/use-auth.ts"
fi

# Fix useCallback.ts
if [ -f hooks/useCallback.ts ]; then
  sed -i "s/import { useCallback as reactUseCallback, DependencyList } from 'react';$/import React, { useCallback as reactUseCallback, DependencyList } from 'react';/" hooks/useCallback.ts
  echo "✅ Fixed hooks/useCallback.ts"
fi

# Fix FileUpload.tsx
if [ -f components/files/FileUpload.tsx ]; then
  sed -i "s/import React, { useState, useRef, useCallback } from 'react'/import React, { useState, useRef, useCallback } from 'react'/" components/files/FileUpload.tsx
  echo "✅ Fixed components/files/FileUpload.tsx"
fi

# Fix documents/[id]/edit/page.tsx if it exists
if [ -f app/documents/\[id\]/edit/page.tsx ]; then
  sed -i "s/import { useState, useEffect, useCallback } from 'react'/import React, { useState, useEffect, useCallback } from 'react'/" app/documents/\[id\]/edit/page.tsx
  echo "✅ Fixed app/documents/[id]/edit/page.tsx"
fi

echo "🎉 All imports fixed!"
