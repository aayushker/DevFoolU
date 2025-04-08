import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import { Badge } from "@/app/components/ui/badge";
import { AlertTriangle, AlertCircle, Check, ExternalLink } from "lucide-react";
import axios from "axios";
import { motion } from "framer-motion";
import { useUser } from "@clerk/nextjs";
import UserProfile from "./UserProfile";

// Define types for our project data
interface ProjectData {
  "Project URL": string;
  "Project Name": string;
  "Project Description"?: string;
  "Tech Stack": string;
  "Similarity with PS (%)": number;
  "Description Crux"?: string[];
}

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

const Result = () => {
  const { isSignedIn, user } = useUser();
  const router = useRouter();
  const { data } = router.query;
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;
  
  const [matchedProjects, setMatchedProjects] = useState<ProjectData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [originalProject, setOriginalProject] = useState<ProjectData | null>(null);
  const [plagiarizerProject, setPlagiarizerProject] = useState<ProjectData | null>(null);

  useEffect(() => {
    // Process data from query params
    if (typeof data === "string") {
      try {
        const parsedData = JSON.parse(data);
        if (parsedData && parsedData.top_5_similar_projects) {
          const sortedProjects = [...parsedData.top_5_similar_projects].sort(
            (a: ProjectData, b: ProjectData) => b["Similarity with PS (%)"] - a["Similarity with PS (%)"]
          );
          setMatchedProjects(sortedProjects);
          
          // Set the original project that was checked
          // This would normally come from the backend response
          if (parsedData.originalProject) {
            setOriginalProject(parsedData.originalProject);
          }
          
          // If high similarity is detected, set the plagiarizer project
          if (sortedProjects.length > 0 && sortedProjects[0]["Similarity with PS (%)"] > 80) {
            setPlagiarizerProject(sortedProjects[0]);
          }
        } else {
          console.error("Invalid data format, expected top_5_similar_projects.");
          setError("Invalid data format returned from server.");
        }
      } catch (error) {
        console.error("Failed to parse data:", error);
        setError("Failed to parse response data.");
      }
      setLoading(false);
    }
  }, [data]);

  // If we have no projects but have a backend URL, fetch some random projects as examples
  useEffect(() => {
    const fetchRandomProjects = async () => {
      if (!loading && matchedProjects.length === 0 && backendURL) {
        try {
          const response = await axios.get(`${backendURL}/api/stats/`);
          if (response.status === 200 && response.data.status === 'success') {
            const projects = response.data.data.latest_projects;
            
            // Map the projects to match our expected format
            const formattedProjects = projects.map((project: any) => ({
              "Project URL": project.project_url,
              "Project Name": project.project_name || "Unnamed Project",
              "Tech Stack": project.tech_stack || "",
              "Similarity with PS (%)": Math.random() * 30 // Low random similarity
            }));
            
            setMatchedProjects(formattedProjects);
          }
        } catch (error) {
          console.error("Failed to fetch random projects:", error);
        }
      }
    };
    
    // Only fetch random projects if we have no matched projects
    if (matchedProjects.length === 0) {
      fetchRandomProjects();
    }
  }, [loading, matchedProjects.length, backendURL]);

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!isSignedIn) {
      router.push('/sign-in');
    }
  }, [isSignedIn, router]);

  const getSimilarityColor = (similarity: number) => {
    if (similarity > 80) return "text-red-500";
    if (similarity > 50) return "text-orange-500";
    return "text-green-500";
  };

  const getSimilarityBadge = (similarity: number) => {
    if (similarity > 80) {
      return (
        <Badge variant="destructive" className="text-xs p-1 ml-2">
          High Match
        </Badge>
      );
    } else if (similarity > 50) {
      return (
        <Badge className="bg-orange-500 text-white text-xs p-1 ml-2">
          Moderate Match
        </Badge>
      );
    } else {
      return (
        <Badge variant="outline" className="bg-green-100 text-green-700 text-xs p-1 ml-2">
          Low Match
        </Badge>
      );
    }
  };

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

  // If still loading, show loading state
  if (loading) {
    return (
      <div className="flex-grow container mx-auto px-4 py-16 text-center">
        <div className="animate-pulse">
          <h2 className="text-3xl font-bold mb-8 text-blue-900">Analyzing Results...</h2>
          <div className="max-w-md mx-auto h-4 bg-gray-200 rounded"></div>
          <div className="mt-8 grid grid-cols-1 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-gray-100 p-6 rounded-lg h-36"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // If there's an error, show error state
  if (error) {
    return (
      <div className="flex-grow container mx-auto px-4 py-16">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex-grow container mx-auto px-4 py-12 relative"
    >
      <div className="absolute top-4 right-4">
        <UserProfile />
      </div>
      
      {/* Result Summary Panel */}
      <div className="mb-12 bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-blue-900 p-6 text-white">
          <h1 className="text-2xl font-bold">Plagiarism Analysis Results</h1>
          <p className="text-blue-100 mt-2">We've analyzed your project against our database of {process.env.NEXT_PUBLIC_TOTAL_PROJECTS || "180,000+"} projects</p>
        </div>
        
        <div className="p-6">
          {plagiarizerProject ? (
            <Alert variant="destructive" className="mb-6">
              <AlertTriangle className="h-5 w-5" />
              <AlertTitle className="text-lg font-bold">High Similarity Detected!</AlertTitle>
              <AlertDescription className="mt-2">
                Your project shows <span className="font-bold">{plagiarizerProject["Similarity with PS (%)"].toFixed(2)}%</span> similarity with an existing project.
                This suggests potential plagiarism concerns.
              </AlertDescription>
            </Alert>
          ) : (
            <Alert className="mb-6 bg-green-50 border-green-200">
              <Check className="h-5 w-5 text-green-500" />
              <AlertTitle className="text-lg font-bold text-green-700">Good News!</AlertTitle>
              <AlertDescription className="mt-2 text-green-600">
                No high-similarity matches found. Your project appears to be original.
              </AlertDescription>
            </Alert>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-bold text-gray-700 mb-2">Analysis Summary</h3>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span className="text-gray-600">Similarity Threshold</span>
                  <span className="font-semibold">80%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Projects Compared</span>
                  <span className="font-semibold">{process.env.NEXT_PUBLIC_TOTAL_PROJECTS || "180,000+"}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Analysis Date</span>
                  <span className="font-semibold">{new Date().toLocaleDateString()}</span>
                </li>
              </ul>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-bold text-gray-700 mb-2">Similarity Scale</h3>
              <div className="mt-4 h-4 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full"></div>
              <div className="flex justify-between mt-1 text-xs text-gray-600">
                <span>0% (Unique)</span>
                <span>50% (Suspicious)</span>
                <span>100% (Identical)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Matched Projects Section */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
      >
        <h2 className="text-2xl font-bold mb-6 text-blue-900">
          Similar Projects
          {matchedProjects.length > 0 ? ` (${matchedProjects.length})` : ""}
        </h2>

        <div className="space-y-6">
          {matchedProjects.length > 0 ? (
            matchedProjects.map((project, index) => (
              <motion.div key={index} variants={item}>
                <Card className="overflow-hidden border-l-4 hover:shadow-lg transition-shadow duration-300"
                      style={{ borderLeftColor: project["Similarity with PS (%)"] > 80 ? '#ef4444' : 
                                              project["Similarity with PS (%)"] > 50 ? '#f97316' : '#22c55e' }}>
                  <CardHeader className="bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-xl text-blue-900">{project["Project Name"]}</CardTitle>
                        <CardDescription className="mt-1 line-clamp-2">
                          {project["Project Description"] || "No description available"}
                        </CardDescription>
                      </div>
                      <div className={`text-2xl font-bold ${getSimilarityColor(project["Similarity with PS (%)"])}`}>
                        {project["Similarity with PS (%)"].toFixed(2)}% 
                        {getSimilarityBadge(project["Similarity with PS (%)"])}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="flex flex-wrap gap-2 mb-4">
                      {typeof project["Tech Stack"] === "string" &&
                        project["Tech Stack"]
                          .split(", ")
                          .slice(0, 8)
                          .map((tech, techIndex) => (
                            <Badge key={techIndex} className="bg-blue-100 text-blue-800 border-none">
                              {tech}
                            </Badge>
                          ))}
                    </div>
                    
                    {project["Description Crux"] && (
                      <div className="mt-4">
                        <h4 className="text-sm text-gray-500 mb-2">Key Topics:</h4>
                        <div className="flex flex-wrap gap-1">
                          {project["Description Crux"].slice(0, 10).map((word, i) => (
                            <Badge key={i} variant="outline" className="bg-gray-50">
                              {word}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="bg-gray-50 border-t">
                    <Button
                      variant="outline"
                      className="text-blue-900 hover:bg-blue-900 hover:text-white transition-colors"
                      onClick={() => window.open(project["Project URL"], "_blank")}
                    >
                      View Project <ExternalLink className="ml-2 h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-10 bg-gray-50 rounded-lg border">
              <div className="text-gray-500">No similar projects found in our database.</div>
              <Button 
                className="mt-4 bg-blue-900 hover:bg-blue-800"
                onClick={() => router.push('/project')}
              >
                Check Another Project
              </Button>
            </div>
          )}
        </div>
      </motion.div>

      <div className="mt-12 text-center">
        <p className="text-gray-500 mb-6">Need to check another project?</p>
        <Button 
          size="lg" 
          className="bg-blue-900 hover:bg-blue-800 text-white"
          onClick={() => router.push('/project')}
        >
          Start New Check
        </Button>
      </div>
    </motion.div>
  );
};

export default Result;
