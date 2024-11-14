"use client";
import { useState } from "react";
import { useRouter } from "next/router";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { Loader2 } from "lucide-react";
import axios from "axios";

const Project = () => {
  const backendURL = process.env.NEXT_PUBLIC_URL;
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    if (!url) {
      return;
    }
    const formData = new FormData();
    formData.append("projectURL", url);
    try {
      const response = await axios.post(`${backendURL}/api/project/`, formData);
      if (response.data.status === "success") {
        router.push({
          pathname: "/result",
          query: { data: JSON.stringify(response.data.data) },
        });
      } else {
        console.error(response.data.message);
      }
    } catch (error) {
      console.error(error);
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-grow flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <h2 className="text-5xl font-bold text-center mb-8 text-blue-900">
            Check Your Project
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="url"
              placeholder="Paste your Devfolio project URL here"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              className="w-full"
            />
            <Button
              type="submit"
              className="w-full bg-teal-500 hover:bg-teal-600 text-white"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking for Plagiarism...
                </>
              ) : (
                "Check for Plagiarism"
              )}
            </Button>
          </form>
          {isLoading && (
            <div className="mt-8">
              <div className="h-2 bg-teal-200 rounded-full">
                <div
                  className="h-2 bg-teal-500 rounded-full animate-pulse"
                  style={{ width: "'60%'" }}
                ></div>
              </div>
              <p className="text-center mt-2 text-sm text-blue-900">
                Analyzing your project...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Project;
