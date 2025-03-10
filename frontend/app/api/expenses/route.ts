import { type NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:3000";
// GET handler for retrieving expenses
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const groupId = searchParams.get("groupId");
    const limit = Number.parseInt(searchParams.get("limit") || "20");

    // Call the Splitwise API to get expenses
    // This is a placeholder - replace with your actual API endpoint
    let url = `${API_BASE_URL}/api/expenses`;

    const params = new URLSearchParams();
    if (groupId) params.append("group_id", groupId);
    params.append("limit", limit.toString());

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch expenses: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({ status: "success", data });
  } catch (error) {
    console.error("Error fetching expenses:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to fetch expenses" },
      { status: 500 }
    );
  }
}

// POST handler for creating expenses
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { description, amount, groupId, splitEqually } = body;

    if (!description || !amount) {
      return NextResponse.json(
        { status: "error", message: "Description and amount are required" },
        { status: 400 }
      );
    }

    // Call the Splitwise API to create an expense
    // This is a placeholder - replace with your actual API endpoint
    const response = await fetch(`${API_BASE_URL}/api/expenses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        description,
        amount,
        group_id: groupId,
        split_equally: splitEqually,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create expense: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({ status: "success", data });
  } catch (error) {
    console.error("Error creating expense:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to create expense" },
      { status: 500 }
    );
  }
}
