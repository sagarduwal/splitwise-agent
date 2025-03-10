"use client"

import Image from "next/image"
import { ArrowRight, Receipt } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ReceiptPreviewProps {
  receiptData: any
  imageUrl: string
  onProceed: () => void
}

export default function ReceiptPreview({ receiptData, imageUrl, onProceed }: ReceiptPreviewProps) {
  return (
    <div className="space-y-6">
      <Tabs defaultValue="details">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="details">Receipt Details</TabsTrigger>
          <TabsTrigger value="image">Receipt Image</TabsTrigger>
        </TabsList>
        <TabsContent value="details" className="space-y-4 pt-4">
          <div>
            <h3 className="text-lg font-medium">Vendor Information</h3>
            <p className="text-muted-foreground">{receiptData.vendor?.name || "Unknown"}</p>
            {receiptData.vendor?.address && (
              <p className="text-sm text-muted-foreground">{receiptData.vendor.address}</p>
            )}
          </div>

          <div>
            <h3 className="text-lg font-medium">Transaction Details</h3>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="text-sm font-medium">Date</p>
                <p className="text-sm text-muted-foreground">{receiptData.transaction?.date || "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Time</p>
                <p className="text-sm text-muted-foreground">{receiptData.transaction?.time || "Unknown"}</p>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="text-lg font-medium">Items</h3>
            <div className="space-y-2 mt-2">
              {receiptData.items?.map((item, index) => (
                <div key={index} className="grid grid-cols-12 text-sm">
                  <div className="col-span-7">{item.name}</div>
                  <div className="col-span-2 text-right">{item.quantity}x</div>
                  <div className="col-span-3 text-right">${item.total_price.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex justify-between">
              <span className="font-medium">Subtotal</span>
              <span>${receiptData.summary?.subtotal.toFixed(2)}</span>
            </div>
            {receiptData.summary?.tax_details?.map((tax, index) => (
              <div key={index} className="flex justify-between text-sm">
                <span>{tax.type || "Tax"}</span>
                <span>${tax.amount.toFixed(2)}</span>
              </div>
            ))}
            <div className="flex justify-between font-bold mt-2">
              <span>Total</span>
              <span>${receiptData.summary?.total.toFixed(2)}</span>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="image" className="flex justify-center pt-4">
          {imageUrl ? (
            <div className="relative w-full max-w-md h-[400px]">
              <Image src={imageUrl || "/placeholder.svg"} alt="Receipt" fill className="object-contain" />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[400px] border border-dashed rounded-md w-full">
              <Receipt className="h-12 w-12 text-muted-foreground" />
              <p className="text-muted-foreground mt-2">No image preview available</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      <div className="flex justify-end">
        <Button onClick={onProceed}>
          Proceed to Split
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

