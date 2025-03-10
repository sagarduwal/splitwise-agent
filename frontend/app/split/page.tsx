"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Check, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/components/ui/use-toast";

const API_BASE_URL = "http://localhost:8000";

export default function SplitPage() {
  const router = useRouter();
  const [receiptData, setReceiptData] = useState(null);
  const [groups, setGroups] = useState([]);
  const [friends, setFriends] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [splitEqually, setSplitEqually] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Get receipt data from session storage
    const storedData = sessionStorage.getItem("receiptData");
    if (storedData) {
      setReceiptData(JSON.parse(storedData));
    } else {
      router.push("/upload");
    }

    // Fetch groups and friends
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [groupsResponse, friendsResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/groups`),
          fetch(`${API_BASE_URL}/api/friends`),
        ]);

        const groupsData = await groupsResponse.json();
        const friendsData = await friendsResponse.json();

        if (groupsData.status === "success") {
          setGroups(groupsData.data);
        }

        if (friendsData.status === "success") {
          setFriends(friendsData.data);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        toast({
          title: "Error",
          description: "Failed to load groups and friends",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const handleSubmit = async () => {
    if (!receiptData) return;

    setIsSubmitting(true);
    try {
      const vendor = receiptData.vendor?.name || "Unknown Vendor";
      const date =
        receiptData.transaction?.date || new Date().toISOString().split("T")[0];
      const total = receiptData.summary?.total || 0;

      const description = `${vendor} - ${date}`;

      const response = await fetch(`${API_BASE_URL}/api/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description,
          amount: total,
          groupId: selectedGroup || undefined,
          splitEqually,
        }),
      });

      const result = await response.json();

      if (result.status === "success") {
        toast({
          title: "Success",
          description: "Expense added to Splitwise",
          variant: "default",
        });

        // Clear session storage
        sessionStorage.removeItem("receiptData");

        // Redirect to home
        router.push("/");
      } else {
        throw new Error(result.message || "Failed to create expense");
      }
    } catch (error) {
      console.error("Error creating expense:", error);
      toast({
        title: "Error",
        description: "Failed to create expense",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || !receiptData) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center items-center min-h-[50vh]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push("/upload")}
          className="mr-2"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Split Expense</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Receipt Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="font-medium">Vendor</p>
                <p className="text-muted-foreground">
                  {receiptData.vendor?.name || "Unknown"}
                </p>
              </div>
              <div>
                <p className="font-medium">Date</p>
                <p className="text-muted-foreground">
                  {receiptData.transaction?.date || "Unknown"}
                </p>
              </div>
              <Separator />
              <div className="space-y-2">
                <p className="font-medium">Items</p>
                {receiptData.items?.map((item, index) => (
                  <div key={index} className="flex justify-between">
                    <span>{item.name}</span>
                    <span>${item.total_price.toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <Separator />
              <div className="flex justify-between font-bold">
                <span>Total</span>
                <span>${receiptData.summary?.total.toFixed(2)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Split Options</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="group">Select Group or Friend</Label>
                <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                  <SelectTrigger id="group">
                    <SelectValue placeholder="Select a group or friend" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="individual">
                      Individual expense
                    </SelectItem>
                    {groups.map((group) => (
                      <SelectItem key={group.id} value={group.id.toString()}>
                        {group.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Split Type</Label>
                <RadioGroup defaultValue="equal">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem
                      value="equal"
                      id="equal"
                      checked={splitEqually}
                      onClick={() => setSplitEqually(true)}
                    />
                    <Label htmlFor="equal">Split equally</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem
                      value="unequal"
                      id="unequal"
                      checked={!splitEqually}
                      onClick={() => setSplitEqually(false)}
                    />
                    <Label htmlFor="unequal">Split by items/amounts</Label>
                  </div>
                </RadioGroup>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Expense...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Create Expense
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
