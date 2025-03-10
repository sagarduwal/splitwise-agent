import { Suspense } from "react"
import Link from "next/link"
import { ArrowRight, Receipt, Users, Settings } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import RecentExpenses from "@/components/recent-expenses"

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col items-center justify-center space-y-4 text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Splitwise Receipt Processor</h1>
        <p className="max-w-[700px] text-muted-foreground">
          Upload receipts from Costco, Kroger, Sam's Club, and more. Split expenses with friends and groups on
          Splitwise.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Card>
          <CardHeader>
            <CardTitle>Upload Receipt</CardTitle>
            <CardDescription>Upload a receipt image for processing</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center items-center h-32">
              <Receipt className="h-16 w-16 text-muted-foreground" />
            </div>
          </CardContent>
          <CardFooter>
            <Button asChild className="w-full">
              <Link href="/upload">
                Upload Receipt <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Manage Groups</CardTitle>
            <CardDescription>View and manage your Splitwise groups</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center items-center h-32">
              <Users className="h-16 w-16 text-muted-foreground" />
            </div>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" className="w-full">
              <Link href="/groups">
                View Groups <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Settings</CardTitle>
            <CardDescription>Configure your account settings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center items-center h-32">
              <Settings className="h-16 w-16 text-muted-foreground" />
            </div>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" className="w-full">
              <Link href="/settings">
                Settings <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tighter">Recent Expenses</h2>
        <Suspense fallback={<div className="text-center py-8">Loading recent expenses...</div>}>
          <RecentExpenses />
        </Suspense>
      </div>
    </div>
  )
}

