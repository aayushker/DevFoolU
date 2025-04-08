"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { Loader2, ExternalLink, AlertCircle, Info, Link as LinkIcon, CheckCircle2 } from "lucide-react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/app/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import { useUser } from "@clerk/nextjs";
import UserProfile from "@/app/components/UserProfile";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

const Project = () => {
  const { isSignedIn, user } = useUser();
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState(0); // 0: initial, 1: validating, 2: analyzing, 3: processing
  const router = useRouter();

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!isSignedIn) {
      router.push('/sign-in');
    }
  }, [isSignedIn, router]);

  // If not signed in, show loading state
  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setStage(1); // Start at validating stage
    
    if (!url) {
      toast.error("Please enter a project URL");
      setIsLoading(false);
      setStage(0);
      return;
    }
    
    if (!backendURL) {
      console.error("Backend URL is undefined. Check your .env.local file.");
      toast.error("Backend URL configuration is missing.");
      setIsLoading(false);
      setStage(0);
      return;
    }

    // Check if URL is from devfolio
    if (!url.includes("devfolio.co") && !url.includes("localhost")) {
      toast.error("Please enter a valid Devfolio project URL");
      setIsLoading(false);
      setStage(0);
      return;
    }

    const formData = new FormData();
    formData.append("projectURL", url);
    
    try {
      console.log("Submitting to:", `${backendURL}/api/project/`);
      
      // Progress through the stages
      setTimeout(() => setStage(2), 1500); // Move to analyzing after 1.5s
      setTimeout(() => setStage(3), 3000); // Move to processing after 3s
      
      const response = await axios.post(`${backendURL}/api/project/`, formData);
      
      if (response.data.status === "success") {
        toast.success("Analysis complete!");
        router.push({
          pathname: "/result",
          query: { data: JSON.stringify(response.data.data) },
        });
      } else {
        console.error(response.data.message);
        toast.error(response.data.message || "Error analyzing project");
      }
    } catch (error) {
      console.error("Error submitting project:", error);
      toast.error("Failed to analyze project. Please try again.");
    }
    
    setIsLoading(false);
    setStage(0);
  };

  // Calculate progress width based on stage
  const getProgressWidth = () => {
    switch (stage) {
      case 1: return "33%";
      case 2: return "66%";
      case 3: return "90%";
      default: return "0%";
    }
  };

  // Get stage message
  const getStageMessage = () => {
    switch (stage) {
      case 1: return "Validating project URL...";
      case 2: return "Extracting project content...";
      case 3: return "Analyzing against database...";
      default: return "Waiting to analyze...";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex flex-col">
      <ToastContainer />
      <div className="absolute top-4 right-4">
        <UserProfile />
      </div>
      <div className="flex-grow flex items-center justify-center p-4 md:p-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-4xl"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 text-blue-900">
            Check Your Project
          </h1>
          <p className="text-gray-600 text-center mb-8 max-w-2xl mx-auto">
            Verify the originality of your Devfolio project by providing the URL below
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
              <Card className="border-2 hover:border-blue-200 transition-all duration-300 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-2xl text-blue-900">Project URL</CardTitle>
                  <CardDescription>
                    Paste your complete Devfolio project URL
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex space-x-2">
                      <div className="flex-grow">
                        <Input
                          type="url"
                          placeholder="https://devfolio.co/projects/your-project-id"
                          value={url}
                          onChange={(e) => setUrl(e.target.value)}
                          required
                          className="w-full text-base py-6 border-2 focus:border-blue-500"
                          disabled={isLoading}
                        />
                      </div>
                      <Button
                        type="submit"
                        className="bg-blue-900 hover:bg-blue-800 text-white py-6 px-8"
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          "Analyze"
                        )}
                      </Button>
                    </div>
                    
                    {isLoading && (
                      <div className="mt-4">
                        <div className="h-2 bg-gray-200 rounded-full">
                          <motion.div
                            initial={{ width: "0%" }}
                            animate={{ width: getProgressWidth() }}
                            transition={{ duration: 0.5 }}
                            className="h-2 bg-blue-900 rounded-full"
                          ></motion.div>
                        </div>
                        <p className="text-center mt-2 text-sm text-blue-900 font-medium">
                          {getStageMessage()}
                        </p>
                      </div>
                    )}
                  </form>
                </CardContent>
                <CardFooter className="flex flex-col items-start border-t bg-gray-50 p-4">
                  <Alert className="w-full mt-2 bg-blue-50 text-blue-800 border-blue-200">
                    <Info className="h-4 w-4" />
                    <AlertTitle>Project URL Format</AlertTitle>
                    <AlertDescription>
                      Make sure your URL looks like: https://devfolio.co/projects/your-project-id
                    </AlertDescription>
                  </Alert>
                </CardFooter>
              </Card>
            </div>
            
            <div className="md:col-span-1">
              <motion.div 
                variants={container}
                initial="hidden"
                animate="show"
              >
                <Card className="mb-6 border-2 hover:border-teal-200 transition-all duration-300 shadow-md">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xl text-blue-900">How It Works</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.ul variants={item} className="space-y-4">
                      <li className="flex items-start space-x-2">
                        <div className="mt-1 bg-blue-100 p-1 rounded-full">
                          <LinkIcon className="h-4 w-4 text-blue-900" />
                        </div>
                        <div className="text-sm">
                          <span className="font-medium">Submit URL:</span> Enter your Devfolio project URL
                        </div>
                      </li>
                      <li className="flex items-start space-x-2">
                        <div className="mt-1 bg-blue-100 p-1 rounded-full">
                          <Loader2 className="h-4 w-4 text-blue-900" />
                        </div>
                        <div className="text-sm">
                          <span className="font-medium">Analyze:</span> We extract and process your project data
                        </div>
                      </li>
                      <li className="flex items-start space-x-2">
                        <div className="mt-1 bg-blue-100 p-1 rounded-full">
                          <CheckCircle2 className="h-4 w-4 text-blue-900" />
                        </div>
                        <div className="text-sm">
                          <span className="font-medium">Results:</span> Get a detailed similarity report
                        </div>
                      </li>
                    </motion.ul>
                  </CardContent>
                </Card>
                
                <Card className="border-2 hover:border-teal-200 transition-all duration-300 shadow-md">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xl text-blue-900">Why Check?</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.ul variants={item} className="space-y-2 text-sm text-gray-600">
                      <li>• Ensure project originality</li>
                      <li>• Protect your intellectual work</li>
                      <li>• Avoid plagiarism concerns</li>
                      <li>• Build credibility and trust</li>
                    </motion.ul>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </div>
          
          <div className="mt-12 text-center text-gray-500 text-sm">
            <p>
              Your project information is handled securely and only used for plagiarism detection purposes.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Project;
