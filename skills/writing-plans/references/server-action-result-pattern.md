# Server Action Result Pattern

## Problem

Server actions in Next.js commonly use this pattern:

```ts
export async function doSomething(): Promise<DataType> {
  try {
    const { data, error } = await db.query(...)
    if (error) throw error
    return transform(data)
  } catch (error) {
    console.error("[v0] Error:", error)
    return []  // or null, or { success: false }
  }
}
```

The caller **cannot distinguish** "empty results" from "the database is down" — both return the same shape. Errors are silently swallowed and the UI shows nothing.

## Solution: Discriminated Union

Use `Result<T, E>` — a type-safe success/failure wrapper:

```ts
export type Result<T, E = string> =
  | { ok: true; data: T }
  | { ok: false; error: E }
```

**Usage in a server action:**

```ts
export async function doSomething(): Promise<Result<DataType>> {
  const { data, error } = await db.query(...)
  if (error) return failure(error.message)
  return success(transform(data))
}
```

**Usage in the caller (client component or another action):**

```ts
const result = await doSomething()
if (!result.ok) {
  toast({ title: "Failed to load", description: result.error, variant: "destructive" })
  return
}
// result.data — typed and guaranteed non-null here
render(result.data)
```

## Helper Functions

```ts
export function success<T>(data: T): Result<T, never> {
  return { ok: true, data }
}
export function failure<E = string>(error: E): Result<never, E> {
  return { ok: false, error }
}
```

## When to Use

- Every server action that currently uses `console.error` + silent default return
- Every function where the caller needs to know whether the operation succeeded
- API route handlers that return JSON responses

## When NOT to Use

- Simple pure utility functions that can't fail (string formatting, math)
- Client-side-only state derived from existing data
- Cases where failure should throw (and be caught by an error boundary)

## Migration Strategy

Don't convert every file at once. Pick one small server action, convert it, update its callers, and use it as the pattern for future conversions. The type system enforces that callers check `result.ok` before accessing `result.data`, so partial adoption is safe.
