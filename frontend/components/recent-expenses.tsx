"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { Card, CardContent } from "@/components/ui/card";

const API_BASE_URL = "http://localhost:8000";

export default function RecentExpenses() {
  const [expenses, setExpenses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchExpenses = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/expenses?limit=5`);
        const result = await response.json();

        if (result.status === "success") {
          setExpenses(result.data);
        }
      } catch (error) {
        console.error("Error fetching expenses:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchExpenses();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (expenses.length === 0) {
    return (
      <Card>
        <CardContent className="py-6">
          <p className="text-center text-muted-foreground">
            No recent expenses found
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div className="divide-y">
          {expenses.map((expense, index) => (
            <div key={index} className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">{expense.description}</h3>
                  <p className="text-sm text-muted-foreground">
                    {expense.group
                      ? `Group: ${expense.group.name}`
                      : "Individual expense"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">${expense.amount.toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(expense.date), {
                      addSuffix: true,
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
