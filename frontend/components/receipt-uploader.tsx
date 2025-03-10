"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Upload, Image, FileText, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ReceiptUploaderProps {
  onUpload: (file: File) => void
  isProcessing: boolean
}

export default function ReceiptUploader({ onUpload, isProcessing }: ReceiptUploaderProps) {
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()

    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0])
    }
  }

  const handleButtonClick = () => {
    inputRef.current?.click()
  }

  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-full p-6 border-2 border-dashed rounded-lg flex flex-col items-center justify-center min-h-[250px] ${
          dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {isProcessing ? (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-12 w-12 text-primary animate-spin" />
            <p className="text-center text-muted-foreground">Processing receipt...</p>
          </div>
        ) : (
          <>
            <input ref={inputRef} type="file" accept="image/*" onChange={handleChange} className="hidden" />
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 rounded-full bg-primary/10">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div className="text-center space-y-2">
                <h3 className="font-medium text-lg">Upload Receipt</h3>
                <p className="text-sm text-muted-foreground">Drag and drop or click to upload</p>
                <p className="text-xs text-muted-foreground">Supports: JPG, PNG, HEIC, PDF</p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={handleButtonClick} variant="outline" size="sm">
                  <Image className="h-4 w-4 mr-2" />
                  Browse Images
                </Button>
                <Button onClick={handleButtonClick} variant="outline" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Browse Files
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
      <p className="mt-4 text-sm text-muted-foreground text-center">
        We support receipts from Costco, Kroger, Sam's Club, and many other retailers.
      </p>
    </div>
  )
}

