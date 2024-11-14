import React from "react";
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
import { AlertTriangle } from "lucide-react";

const Result = () => {
  const router = useRouter();
  const { data } = router.query;

  let matchedProjects: Array<any> = [];

  if (typeof data === "string") {
    try {
      const parsedData = JSON.parse(data);

      if (parsedData && parsedData.top_5_similar_projects) {
        matchedProjects = parsedData.top_5_similar_projects;
      } else {
        console.error("Invalid data format, expected top_5_similar_projects.");
      }
    } catch (error) {
      console.error("Failed to parse data:", error);
    }
  }

  return (
    <div className="flex-grow container mx-auto px-4 py-8">
      {matchedProjects.length > 0 && (
        <Alert variant="destructive" className="mb-8">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>High Similarity Detected</AlertTitle>
          <AlertDescription>
            {matchedProjects[0]["Similarity with PS (%)"].toFixed(2) > 80 &&
              `${matchedProjects[0]["Similarity with PS (%)"]}` +
                "% similarity detected with an existing project!"}
          </AlertDescription>
        </Alert>
      )}

      <h2 className="text-2xl font-bold mb-6 text-blue-900">
        Matched Projects
      </h2>

      <div className="space-y-6">
        {matchedProjects.length > 0 ? (
          matchedProjects.map((project: any, index: React.Key) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle>{project["Project Name"]}</CardTitle>
                <CardDescription>
                  {project["Project Description"]}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <div className="space-x-2">
                    {typeof project["Tech Stack"] === "string" &&
                      project["Tech Stack"]
                        .split(", ")
                        .map((tech, techIndex) => (
                          <Badge key={techIndex} variant="secondary">
                            {tech}
                          </Badge>
                        ))}
                  </div>
                  <span className="text-2xl font-bold text-red-500">
                    {project["Similarity with PS (%)"].toFixed(2)}% Match
                  </span>
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  variant="outline"
                  onClick={() => window.open(project["Project URL"], "_blank")}
                >
                  View Project
                </Button>
              </CardFooter>
            </Card>
          ))
        ) : (
          <p>No matched projects found.</p>
        )}
      </div>

      <div className="mt-8 text-center">
        <Button size="lg" className="bg-blue-900 hover:bg-blue-800 text-white">
          View Full Report
        </Button>
      </div>
    </div>
  );
};

export default Result;
