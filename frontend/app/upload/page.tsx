"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ReceiptUploader from "@/components/receipt-uploader";
import ReceiptPreview from "@/components/receipt-preview";

export default function UploadPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("upload");
  const [isProcessing, setIsProcessing] = useState(false);
  const [receiptData, setReceiptData] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  const handleUpload = async (file) => {
    if (!file) return;

    setIsProcessing(true);
    setUploadedImage(URL.createObjectURL(file));

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/api/receipts/process",
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();

      if (result.status === "success") {
        setReceiptData(result.data);
        setActiveTab("preview");
      } else {
        throw new Error(result.message || "Failed to process receipt");
      }
    } catch (error) {
      console.error("Error processing receipt:", error);
      // Handle error state here
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProceedToSplit = () => {
    if (receiptData) {
      // Store receipt data in session storage or state management
      sessionStorage.setItem("receiptData", JSON.stringify(receiptData));
      router.push("/split");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push("/")}
          className="mr-2"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Upload Receipt</h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="preview" disabled={!receiptData}>
            Preview
          </TabsTrigger>
        </TabsList>
        <TabsContent value="upload">
          <Card>
            <CardContent className="pt-6">
              <ReceiptUploader
                onUpload={handleUpload}
                isProcessing={isProcessing}
              />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="preview">
          <Card>
            <CardContent className="pt-6">
              {receiptData && (
                <ReceiptPreview
                  receiptData={receiptData}
                  imageUrl={uploadedImage}
                  onProceed={handleProceedToSplit}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
