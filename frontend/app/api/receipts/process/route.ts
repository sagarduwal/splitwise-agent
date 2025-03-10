import { type NextRequest, NextResponse } from "next/server";

const API_URL = "http://localhost:8000/api";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        { status: "error", message: "No file provided" },
        { status: 400 }
      );
    }

    // Convert file to FormData for the API request
    const apiFormData = new FormData();
    apiFormData.append("file", file);

    // Call the receipt processing agent API
    // This is a placeholder - replace with your actual API endpoint
    const response = await fetch(`${API_URL}/receipts/process`, {
      method: "POST",
      body: apiFormData,
    });

    if (!response.ok) {
      throw new Error(`Receipt processing failed: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({ status: "success", data });
  } catch (error) {
    console.error("Error processing receipt:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to process receipt" },
      { status: 500 }
    );
  }
}
