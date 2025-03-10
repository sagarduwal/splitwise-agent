import { type NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:3000";

export async function GET(request: NextRequest) {
  try {
    // Call the Splitwise API to get friends
    // This is a placeholder - replace with your actual API endpoint
    const response = await fetch(`${API_BASE_URL}/api/friends`);

    if (!response.ok) {
      throw new Error(`Failed to fetch friends: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({ status: "success", data });
  } catch (error) {
    console.error("Error fetching friends:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to fetch friends" },
      { status: 500 }
    );
  }
}
