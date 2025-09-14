import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function App() {
  const [count, setCount] = useState(0)

  return (
    <main className="min-h-screen bg-background text-foreground flex items-center">
      <div className="container">
        <Card className="mx-auto max-w-xl shadow-lg">
          <CardContent className="p-8">
            <h1 className="text-3xl font-semibold mb-4">
              Hybrid AI Platform — Hello World
            </h1>
            <p className="text-muted-foreground mb-6">
              Vite + React + TypeScript + Tailwind + shadcn/ui
            </p>
            <div className="flex items-center gap-3">
              <Button onClick={() => setCount((c) => c + 1)}>Click me</Button>
              <span>Count: {count}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
